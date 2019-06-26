import re
from dataclasses import dataclass, field
from io import BytesIO
from typing import Dict, Union
from urllib.parse import parse_qsl

HTTP_200 = "200 OK"
HTTP_302 = "302 Found"
HTTP_403 = "403 Forbidden"
HTTP_404 = "404 Not Found"
HTTP_405 = "405 Method Not Allowed"
HTTP_410 = "410 Gone"


def format_environ_header(name):
    return name.lower().replace("http_", "").replace("_", "-")


def make_request_headers(environ):
    return {
        "content-length": environ.get("CONTENT_LENGTH", "0"),
        "content-type": environ.get("CONTENT_TYPE", "application/octet-stream"),
        **{
            format_environ_header(name): value
            for name, value in environ.items() if name.startswith("HTTP_")
        }
    }


@dataclass
class Request:
    method: str
    path: str
    params: Dict[str, str]
    headers: Dict[str, str]
    body: BytesIO

    _post_data: Dict[str, str] = None

    @classmethod
    def from_environ(cls, environ):
        return cls(
            method=environ["REQUEST_METHOD"],
            path=environ["PATH_INFO"],
            params=dict(parse_qsl(environ.get("QUERY_STRING", ""))),
            headers=make_request_headers(environ),
            body=environ["wsgi.input"],
        )

    @property
    def post_data(self):
        if self._post_data is None:
            parsed_data = parse_qsl(self.body.read(int(self.headers.get("content-length"))))
            self._post_data = {
                name.decode("utf-8"): value.decode("utf-8") for name, value in parsed_data
            }

        return self._post_data


def make_response_headers():
    return [
        ("Content-type", "text/html; charset=utf-8")
    ]


@dataclass
class Response:
    status: str = HTTP_200
    headers: list = field(default_factory=make_response_headers)
    content: Union[bytes, str, BytesIO] = field(default_factory=BytesIO)

    def add_header(self, name, value):
        self.headers.append((name, value))

    def __iter__(self):
        if isinstance(self.content, str):
            return iter([self.content.encode("utf-8")])

        elif isinstance(self.content, bytes):
            return iter([self.content])

        else:
            return self.content


def make_response(value):
    if isinstance(value, str):
        return Response(content=value)

    elif isinstance(value, tuple) and len(value) == 2:
        return Response(status=value[0], content=value[1])

    else:
        return value


class App:
    def __init__(self):
        self._dispatch_table = []

    def add_route(self, pattern, handler):
        self._dispatch_table.append((re.compile(f"^{pattern}/?$"), handler))

    def __call__(self, environ, start_response):
        request = Request.from_environ(environ)
        for path_re, path_handler in self._dispatch_table:
            match = path_re.match(request.path)
            if match:
                return path_handler(request, start_response, **match.groupdict())


def handler(fn):
    def wrapper(self, request, start_response, *args, **kwargs):
        response = make_response(fn(self, request, *args, **kwargs))
        start_response(response.status, response.headers)
        return response
    return wrapper


def templated(template_name):
    def decorator(fn):
        def wrapper(self, request, *args, **kwargs):
            response = fn(self, request, *args, **kwargs)
            if isinstance(response, Response):
                return response

            context = {"request": request, **response}
            return self.templates.get_template(template_name).render(context)
        return wrapper
    return decorator


def redirect(uri):
    response = Response(status=HTTP_302)
    response.add_header("location", uri)
    return response
