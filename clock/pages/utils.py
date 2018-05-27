from datetime import datetime, timedelta

from django.utils import timezone


def round_time(dt=None, obj=None, date_delta=timedelta(minutes=5), to="average"):
    """Round a datetime object to a multiple of a timedelta

    dt : datetime.datetime object, default now.

    dateDelta : timedelta object, we round to a multiple of this, default 5
    minute.

    from:
    http://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python

    """
    round_to = date_delta.total_seconds()

    if dt is None:
        dt = timezone.now()

    if isinstance(dt, datetime):
        tzmin = dt.min.replace(tzinfo=dt.tzinfo)
        obj = "dt"
    if isinstance(dt, timedelta):
        tzmin = dt.min
        obj = "td"
    seconds = (dt - tzmin).seconds

    if to == "up":
        rounding = (seconds + round_to) // round_to * round_to
    elif to == "down":
        rounding = seconds // round_to * round_to
    else:
        rounding = (seconds + round_to / 2) // round_to * round_to
    if obj == "dt":
        return dt + timedelta(0, rounding - seconds, -dt.microsecond)
    elif obj == "td":
        return (
            dt
            + timedelta(0, rounding - seconds)
            - timedelta(microseconds=dt.microseconds)
        )
