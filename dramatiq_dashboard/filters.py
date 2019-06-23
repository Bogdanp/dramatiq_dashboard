from datetime import datetime


def isoformat(dt):
    return dt.isoformat()


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
        if delta > scale:
            delta //= scale

        else:
            break

    return f"{delta}{_label} ago"
