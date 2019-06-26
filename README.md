# dramatiq_dashboard

A dashboard for [dramatiq], specific to its Redis broker (sorry
RabbitMQ users!).  Very alpha stuff.

It comes in the form of a WSGI middleware, with as few dependencies as
possible (`dramatiq`, `jinja2` and `redis`) so it's super easy to plug
into whatever web application you have.

![screencast](https://media.defn.io/dramatiq-dashboard-screencast.gif)

## Installation

    pip install dramatiq_dashboard

## Supporting the Project

If you use and love Dramatiq and want to make sure it gets the love
and attention it deserves then you should consider supporting the
project.  There are three ways in which you can do this right now:

1. If you're a company that uses Dramatiq in production then you can
   get a [Tidelift] subscription.  Doing so will give you an easy
   route to supporting both Dramatiq and other open source projects
   that you depend on.
2. If you're an individual or a company that doesn't want to go
   through Tidelift then you can support the project via [Patreon].
3. If you're a company and neither option works for you and you would
   like to receive an invoice from me directly then email me at
   bogdan@defn.io and let's talk.

[Tidelift]: https://tidelift.com/subscription/pkg/pypi-dramatiq?utm_source=pypi-dramatiq&utm_medium=referral&utm_campaign=readme
[Patreon]: https://patreon.com/popabogdanp

## Quickstart

#### Run the dashboard on top of an existing WSGI app

```python
# Assuming at some point you instantiate your app.
app = create_wsgi_application()

# Import the library, create the middleware and wrap your app with it.
import dramatiq_dashboard

dashboard_middleware = dramatiq_dashboard.make_wsgi_middleware("/drama")
app = dashboard_middleware(app)
```

Run your app, visit `/drama` and you should see the dashboard.

#### Run the dashboard as a standalone webserver

If you don't want to wrap an existing WSGI app, you can also run the
dashboard as a standalone server.  Install the WSGI server of your
choice (e.g. uWSGi, gunicorn, bjoern, etc), setup the Redis broker,
and then start `DashboardApp` directly.

For example, to serve the dashboard on `http://127.0.0.1:8080` using
the `bjoern` WSGI server and a redis server on `17.0.0.1:6379`, run
the following:

```python
import bjoern
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq_dashboard import DashboardApp

broker = RedisBroker(host="127.0.0.1", port=6379)
dramatiq.set_broker(broker)
app = DashboardApp(broker=broker, prefix="")
bjoern.run(app, "127.0.0.1", 8080)
```

Then visit http://127.0.0.1:8080/ to see the running dashboard.

*Note that if you use custom queues in your application, they won't be
discovered using this approach.  You'll have to either add each one of
them manually to your broker or import and pass your application's
broker to `DashboardApp`.*

## License

dramatiq_dashboard is licensed under the LGPL.  Please see [COPYING]
and [COPYING.LESSER] for licensing details.


[COPYING.LESSER]: https://github.com/Bogdanp/dramatiq_dashboard/blob/master/COPYING.LESSER
[COPYING]: https://github.com/Bogdanp/dramatiq_dashboard/blob/master/COPYING
[dramatiq]: https://dramatiq.io
