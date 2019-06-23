import re
from urllib.request import urlopen

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from molten import App, QueryParam, Route

import dramatiq_dashboard

broker = RedisBroker()
dramatiq.set_broker(broker)

HREF_RE = re.compile('href="(https?://[^"]+)"')


@dramatiq.actor(max_retries=1)
def crawl(uri):
    crawl.logger.info("Crawling %r...", uri)
    with urlopen(uri) as response:
        if "text/html" not in response.headers.get("content-type", ""):
            return

        for match in HREF_RE.finditer(response.read().decode("utf-8")):
            match_uri = match.group(1)
            if broker.client.sismember("crawl_seen", match_uri):
                continue

            crawl.send(match_uri)
            broker.client.sadd("crawl_seen", match_uri)


def start(uri: QueryParam):
    if not uri.startswith("http"):
        uri = f"http://{uri}"

    crawl.send(uri)
    return "Message sent!"


app = App(
    routes=[
        Route("/crawl", start)
    ]
)

dashboard_middleware = dramatiq_dashboard.make_wsgi_middleware("/drama")
app = dashboard_middleware(app)
