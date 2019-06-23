from datetime import datetime


def isoformat(dt):
    return dt.isoformat()


def short(n):
    levels = [
        (None, 1000.0),
        ("K", 1000.0),
        ("M", float("inf")),
    ]

    for _label, scale in levels:
        if n >= scale:
            n /= scale

        else:
            break

    if _label:
        return f"{n:0.2f}{_label}"
    return str(n)


def timeago(dt):
    delta = round((datetime.utcnow() - dt).total_seconds() * 1000)
    levels = [
        ("us", 1),
        ("ms", 1000),
        ("s", 60),
        ("m", 60),
        ("h", 24),
        ("d", 7),
        ("w", 4),
        ("M", 12),
        ("Y", float("inf")),
    ]

    for _label, scale in levels:
        if abs(delta) > scale:
            delta //= scale

        else:
            break

    if delta < 0:
        return f"in {abs(delta)}{_label}"

    else:
        return f"{delta}{_label} ago"
