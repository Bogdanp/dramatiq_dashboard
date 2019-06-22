from dataclasses import dataclass, field
from io import BytesIO
from typing import Dict, Union
from urllib.parse import parse_qsl

HTTP_200 = "200 OK"
HTTP_302 = "302 Found"
HTTP_403 = "403 Forbidden"
HTTP_404 = "404 Not Found"
HTTP_405 = "405 Method Not Allowed"


def make_headers():
    return [
        ("Content-type", "text/html; charset=utf-8")
    ]


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
            params=dict(parse_qsl(environ["QUERY_STRING"])),
            headers={
                "content-length": environ.get("CONTENT_LENGTH", "0"),
                "content-type": environ.get("CONTENT_TYPE", "application/octet-stream"),
                **{
                    name.lower().replace("HTTP_", "").replace("_", "-"): value
                    for name, value in environ.items() if name.startswith("HTTP_")
                }
            },
            body=environ["wsgi.input"],
        )

    @property
    def post_data(self):
        if self._post_data is None:
            parsed_data = parse_qsl(self.body.read(int(self.headers.get("content-length"))))
            self._post_data = {name.decode("utf-8"): value.decode("utf-8") for name, value in parsed_data}

        return self._post_data


@dataclass
class Response:
    status: str = HTTP_200
    headers: list = field(default_factory=make_headers)
    content: Union[bytes, str, BytesIO] = field(default_factory=BytesIO)

    def __iter__(self):
        if isinstance(self.content, str):
            return iter([self.content.encode("utf-8")])

        elif isinstance(self.content, bytes):
            return iter([self.content])

        else:
            return self.content


def handler(fn):
    def wrapper(self, environ, start_response, *args, **kwargs):
        request = Request.from_environ(environ)
        response = fn(self, request, *args, **kwargs)
        if isinstance(response, str):
            response = Response(content=response)

        elif isinstance(response, tuple) and len(response) == 2:
            response = Response(status=response[0], content=response[1])

        start_response(response.status, response.headers)
        return response
    return wrapper


def templated(template_name):
    def decorator(fn):
        def wrapper(self, request, *args, **kwargs):
            context = {
                "request": request,
                **fn(self, request, *args, **kwargs)
            }
            return self.templates.get_template(template_name).render(context)
        return wrapper
    return decorator
