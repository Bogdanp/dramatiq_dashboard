import random
from time import sleep

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from molten import App, Route

import dramatiq_dashboard

broker = RedisBroker()
dramatiq.set_broker(broker)


@dramatiq.actor(max_retries=2)
def perform(n):
    if n % 2 == 0:
        raise RuntimeError("an error")

    sleep(n)
    perform.logger.info("Task done!")


def home():
    for _ in range(100):
        perform.send(random.randint(1, 100))

    return "Task enqueued!"


app = App(
    routes=[
        Route("/", home)
    ]
)

dashboard_middleware = dramatiq_dashboard.make_wsgi_middleware("/drama")
app = dashboard_middleware(app)
