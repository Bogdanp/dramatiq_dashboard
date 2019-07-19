import pytest

from dramatiq_dashboard import csrf
from dramatiq_dashboard.http import Request

TEST_CSRF_TOKEN = csrf.generate_csrf_token()

@pytest.mark.parametrize(
    "cookie,expected",
    [
        (f'{csrf._CSRF_COOKIE}={TEST_CSRF_TOKEN}', TEST_CSRF_TOKEN),
        (f'some_other_cookie=true {csrf._CSRF_COOKIE}={TEST_CSRF_TOKEN}', TEST_CSRF_TOKEN),
        (f'{csrf._CSRF_COOKIE}={TEST_CSRF_TOKEN} some_other_cookie=true', TEST_CSRF_TOKEN),
        (f'the_first_cookie=asdf {csrf._CSRF_COOKIE}={TEST_CSRF_TOKEN} some_other_cookie=true', TEST_CSRF_TOKEN),
    ]
)
def test_lookup_csrf_token(cookie, expected):
    req = Request.test_request(headers={'cookie': cookie})
    assert csrf.lookup_csrf_token(req) == expected
