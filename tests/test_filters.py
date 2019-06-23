from datetime import datetime, timedelta

import pytest

from dramatiq_dashboard.filters import short, timeago


@pytest.mark.parametrize(
    "n,expected",
    [
        (1, "1"),
        (100, "100"),
        (1000, "1.00K"),
        (1350, "1.35K"),
        (1000000, "1.00M"),
        (1050000, "1.05M"),
    ]
)
def test_short(n, expected):
    assert short(n) == expected


@pytest.mark.parametrize(
    "delta,expected",
    [
        (timedelta(seconds=-35), "in 35s"),
        (timedelta(seconds=35), "35s ago"),
        (timedelta(minutes=-2), "in 2m"),
        (timedelta(minutes=2), "2m ago"),
        (timedelta(minutes=-42), "in 42m"),
        (timedelta(minutes=42), "42m ago"),
        (timedelta(minutes=-67), "in 1h"),
        (timedelta(minutes=67), "1h ago"),
        (timedelta(hours=-8), "in 8h"),
        (timedelta(hours=8), "8h ago"),
        (timedelta(days=-2), "in 2d"),
        (timedelta(days=2), "2d ago"),
        (timedelta(days=-9), "in 1w"),
        (timedelta(days=9), "1w ago"),
        (timedelta(weeks=-5), "in 1M"),
        (timedelta(weeks=5), "1M ago"),
        (timedelta(weeks=-52), "in 1Y"),
        (timedelta(weeks=52), "1Y ago"),
    ]
)
def test_timeago(delta, expected):
    dt = datetime.utcnow() - delta
    assert timeago(dt) == expected
