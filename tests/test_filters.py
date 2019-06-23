from datetime import datetime, timedelta

import pytest

from dramatiq_dashboard.filters import timeago


@pytest.mark.parametrize(
    "delta,expected",
    [
        (timedelta(seconds=35), "35s ago"),
        (timedelta(minutes=2), "2m ago"),
        (timedelta(minutes=42), "42m ago"),
        (timedelta(minutes=67), "1h ago"),
        (timedelta(hours=8), "8h ago"),
        (timedelta(days=2), "2d ago"),
        (timedelta(days=9), "1w ago"),
        (timedelta(weeks=5), "1M ago"),
        (timedelta(weeks=52), "1Y ago"),
    ]
)
def test_timeago(delta, expected):
    dt = datetime.utcnow() - delta
    assert timeago(dt) == expected
