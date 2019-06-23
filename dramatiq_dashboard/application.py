from pprint import pformat
from urllib.parse import urlencode

import jinja2
from dramatiq.common import dq_name, q_name, xq_name

from .csrf import csrf_protect, render_csrf_token
from .filters import isoformat, short, timeago
from .http import HTTP_404, HTTP_405, HTTP_410, App, handler, redirect, templated
from .interface import Job, RedisInterface


def make_uri_maker(prefix):
    def make_uri(*path_segments, params=None):
        uri = f"{prefix}/{'/'.join(str(segment) for segment in path_segments)}"
        if params is not None:
            uri += f"?{urlencode(params)}"

        return uri
    return make_uri


def tab_from_q_name(name):
    if name == dq_name(name):
        return "delayed"

    elif name == xq_name(name):
        return "failed"

    else:
        return "standard"


def queue_for_tab(name, tab):
    return {
        "standard": name,
        "delayed": dq_name(name),
        "failed": xq_name(name),
    }[tab]


class DashboardApp(App):
    def __init__(self, broker, prefix):
        super().__init__()

        self.broker = broker
        self.iface = RedisInterface(broker)
        self.make_uri = make_uri = make_uri_maker(prefix)

        self.templates = jinja2.Environment(
            loader=jinja2.PackageLoader("dramatiq_dashboard", "templates"),
            autoescape=jinja2.select_autoescape(["html"]),
            auto_reload=False,
        )
        self.templates.filters.update({
            "isoformat": isoformat,
            "pformat": pformat,
            "short": short,
            "timeago": timeago,
        })
        self.templates.globals.update({
            "csrf_token": render_csrf_token,
            "make_uri": make_uri,
        })

        self.add_route("/", self.dashboard)
        self.add_route("/queues/(?P<name>[^/]+)", self.queue)
        self.add_route("/queues/(?P<name>[^/]+)/(?P<current_tab>(standard|delayed|failed))", self.queue)
        self.add_route("/queues/(?P<name>[^/]+)/(?P<current_tab>(standard|delayed|failed))/(?P<message_id>[^/]+)", self.job)
        self.add_route("/delete-message", self.delete_message)
        self.add_route("/requeue-message", self.requeue_message)
        self.add_route(".*", self.not_found)

    @handler
    @templated("dashboard.html")
    def dashboard(self, req):
        return {
            "queues": self.iface.queues,
            "workers": self.iface.workers
        }

    @handler
    @csrf_protect
    @templated("queue.html")
    def queue(self, req, *, name, current_tab="standard"):
        cursor = int(req.params.get("cursor", 0))
        qft = queue_for_tab(name, current_tab)

        queue = self.iface.get_queue(q_name(name))
        next_cursor, jobs = self.iface.get_jobs(qft, cursor)
        return {
            "queue": queue,
            "jobs": jobs,
            "cursor": next_cursor,
            "current_tab": current_tab,
            "queue_for_tab": qft,
        }

    @handler
    @csrf_protect
    @templated("job.html")
    def job(self, req, *, name, current_tab, message_id):
        qft = queue_for_tab(name, current_tab)
        queue = self.iface.get_queue(q_name(name))
        job = self.iface.get_job(qft, message_id)
        if not job:
            return redirect(self.make_uri("queues", name, current_tab))

        return {
            "queue": queue,
            "job": job,
            "queue_for_tab": qft,
        }

    @handler
    @csrf_protect
    def delete_message(self, req):
        if req.method != "POST":
            return HTTP_405, "Expected a POST request."

        queue = req.post_data["queue"]
        message_id = req.post_data["id"]
        self.iface.delete_message(queue, message_id)

        return redirect(self.make_uri("queues", q_name(queue), tab_from_q_name(queue)))

    @handler
    @csrf_protect
    def requeue_message(self, req):
        if req.method != "POST":
            return HTTP_405, "Expected a POST request."

        queue = req.post_data["queue"]
        message_id = req.post_data["id"]
        job = self.iface.get_job(queue, message_id)
        if not job:
            return HTTP_410, "The requested message no longer exists."

        self.iface.delete_message(queue, message_id)
        job_copy = Job.from_message(self.broker.enqueue(job.message.copy(
            queue_name=q_name(queue),
            options={
                "eta": job.message_timestamp,
                "retries": 0
            },
        )))
        return redirect(self.make_uri(
            "queues",
            q_name(queue),
            tab_from_q_name(queue),
            job_copy.message_id,
        ))

    @handler
    def not_found(self, req):
        return HTTP_404, "Not Found"
