# basic example

This example combines, [molten], [dramatiq] and [dramatiq_dashboard]
together into a basic web app.


## Setup

    pip install -r requirements.txt


## Running

In one terminal, run the web server:

    gunicorn app:app

In another, run dramatiq:

    dramatiq app


[dramatiq]: https://dramatiq.io
[molten]: https://moltenframework.com
