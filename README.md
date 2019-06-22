# dramatiq_dashboard

A dashboard for [dramatiq], specific to its Redis broker (sorry
RabbitMQ users!).  Very alpha stuff.

It comes in the form of a WSGI middleware, with as few dependencies as
possible (`dramatiq`, `jinja2` and `redis`) so it's super easy to plug
into whatever web application you have.

![screencast](/media/screencast.gif)

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

```python
# Assuming at some point you instantiate your app.
app = create_wsgi_application()


# Import the library, create the middleware and wrap your app with it.
import dramatiq_dashboard

dashboard_middleware = dramatiq_dashboard.make_wsgi_middleware("/drama")
app = dashboard_middleware(app)
```

Run your app, visit `/drama` and you should see the dashboard.

## License

dramatiq_dashboard is licensed under the LGPL.  Please see [COPYING]
and [COPYING.LESSER] for licensing details.


[COPYING.LESSER]: https://github.com/Bogdanp/dramatiq_dashboard/blob/master/COPYING.LESSER
[COPYING]: https://github.com/Bogdanp/dramatiq_dashboard/blob/master/COPYING
[dramatiq]: https://dramatiq.io
