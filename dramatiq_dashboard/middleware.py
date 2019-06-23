import dramatiq
from dramatiq.brokers.redis import RedisBroker

from .application import DashboardApp


class DashboardMiddleware:
    def __init__(self, app, broker, prefix):
        self.app = app
        self.prefix = prefix
        self.dashboard_app = DashboardApp(broker, prefix)

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path.startswith(self.prefix):
            app_environ = {**environ, "PATH_INFO": path[len(self.prefix):]}
            return self.dashboard_app(app_environ, start_response)

        return self.app(environ, start_response)


def make_wsgi_middleware(prefix, broker=None):
    broker = broker or dramatiq.get_broker()
    if not isinstance(broker, RedisBroker):
        raise RuntimeError("broker must be a RedisBroker")

    def middleware(app):
        return DashboardMiddleware(app, broker, prefix)
    return middleware
