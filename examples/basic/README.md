# basic example

This example combines, [molten], [dramatiq] and [dramatiq_dashboard]
together into a basic web app.


## Setup

    pip install -r requirements.txt


## Running

In one terminal, run the web server:

    gunicorn app:app

In another, run dramatiq:

    dramatiq app -p 2 -t 2

Visit https://localhost:8000/crawl?uri=news.ycombinator.com to start
the crawler then visit https://localhost:8000/drama/ to see the
dashboard.


[dramatiq]: https://dramatiq.io
[molten]: https://moltenframework.com
