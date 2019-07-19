import os
import re
from threading import local

from .http import HTTP_403, make_response

_CSRF_COOKIE = "__dd_csrf"
_CSRF_COOKIE_RE = re.compile(f"{_CSRF_COOKIE}=([^;]+)")
_CSRF_STATE = local()


def render_csrf_token():
    token = getattr(_CSRF_STATE, "token", "")
    return f'<input type="hidden" name="{_CSRF_COOKIE}" value="{token}">'


def generate_csrf_token():
    return "".join(f"{b:02x}" for b in os.urandom(32))


def lookup_csrf_token(request):
    cookies = request.headers.get("cookie")
    if cookies:
        match = _CSRF_COOKIE_RE.search(cookies)
        if match:
            return match.group(1)

    return generate_csrf_token()


def csrf_protect(fn):
    def wrapper(self, request, *args, **kwargs):
        token = lookup_csrf_token(request)
        setattr(_CSRF_STATE, "token", token)

        if request.method == "POST":
            request_token = request.post_data.get(_CSRF_COOKIE)
            if request_token != token:
                return HTTP_403, "Forbidden"

        response = make_response(fn(self, request, *args, **kwargs))
        response.headers.append(("set-cookie", f"{_CSRF_COOKIE}={token}; HttpOnly; Path=/"))
        return response
    return wrapper
