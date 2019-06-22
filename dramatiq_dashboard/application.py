import re
from urllib.parse import urlencode

import jinja2
from dramatiq.common import dq_name, q_name, xq_name

from .filters import isoformat, timeago
from .http import HTTP_302, HTTP_404, HTTP_405, Response, handler, templated
from .interface import RedisInterface


class DashboardApp:
    def __init__(self, broker, prefix):
        self.iface = RedisInterface(broker)
        self.prefix = prefix

        self.dispatch_table = [
            (re.compile(f"^/?$"), self.dashboard),
            (re.compile(f"^/queues/(?P<name>[^/]+)/?$"), self.queue),
            (re.compile(f"^/queues/(?P<name>[^/]+)/(?P<current_tab>(standard|delayed|failed))/?$"), self.queue),
            (re.compile(f"^/delete-message/?$"), self.delete_message),
            (re.compile(f"^.*$"), self.not_found),
        ]

        self.templates = jinja2.Environment(
            loader=jinja2.PackageLoader("dramatiq_dashboard", "templates"),
            autoescape=jinja2.select_autoescape(["html"]),
            auto_reload=False,
        )
        self.templates.filters.update({
            "isoformat": isoformat,
            "timeago": timeago,
        })
        self.templates.globals.update({
            "make_uri": self.make_uri,
        })

    def __call__(self, path, environ, start_response):
        for path_re, path_handler in self.dispatch_table:
            match = path_re.match(path)
            if match:
                return path_handler(environ, start_response, **match.groupdict())

    def make_uri(self, *path_segments, params=None):
        uri = f"{self.prefix}/{'/'.join(str(segment) for segment in path_segments)}"
        if params is not None:
            uri += f"?{urlencode(params)}"

        return uri

    @handler
    @templated("dashboard.html")
    def dashboard(self, req):
        return {
            "queues": self.iface.queues,
            "workers": self.iface.workers
        }

    @handler
    @templated("queue.html")
    def queue(self, req, *, name, current_tab="standard"):
        cursor = int(req.params.get("cursor", 0))
        queue_for_tab = {
            "standard": name,
            "delayed": dq_name(name),
            "failed": xq_name(name),
        }[current_tab]

        next_cursor, jobs = self.iface.get_jobs(queue_for_tab, cursor)
        return {
            "name": name,
            "jobs": jobs,
            "cursor": next_cursor,
            "current_tab": current_tab,
            "queue_for_tab": queue_for_tab,
        }

    @handler
    def delete_message(self, req):
        if req.method != "POST":
            return HTTP_405, "Expected a POST request."

        queue = req.post_data["queue"]
        message_id = req.post_data["id"]
        self.iface.delete_message(queue, message_id)
        return Response(
            status=HTTP_302,
            headers=[
                ("location", self.make_uri("queues", q_name(queue)))
            ]
        )

    @handler
    def not_found(self, req):
        return HTTP_404, "Not Found"
