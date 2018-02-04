import time
from datetime import datetime, timedelta

from django import template

register = template.Library()


@register.filter()
def format_dttd(t, t_format="%H:%M:%S"):
    """Should be used to format a given datetime or timedelta (hence dttd) to a
    specific format.

    Parameter
    ---------
    t: datetime
        Datetime or timedelta object

    t_format: str
        Format the object should be returned as (e.g. "%H:%M" for 23:15)

    Returns
    -------
    String of the formatted dt/td object

    """
    if isinstance(t, timedelta):
        value = time.strftime(
            t_format, time.gmtime(t.seconds + t.days * 86400)
        )
        if t.days > 0:
            hours = t.days * 24
            s = value.split(':')
            if 1 < len(s) < 4:
                value = str(int(value[0:2]) + hours) + value[2:]
            elif len(s) == 1:
                value = int(s[0]) + hours
            else:
                raise ValueError(
                    'We are having a problem handling the input {} and'
                    'converting it into {}.'.format(str(t), t_format)
                )
        return value
    if isinstance(t, datetime):
        return t.strftime(t_format)
    # raise ValueError(
    # 'The provided object {} does not match any accepted classes.'.
    # format(t)
    # )


@register.filter
def format_week(date):
    # Django docs says we should not use built-in |date template filter to
    # display week numbers. See:
    # https://docs.djangoproject.com/en/1.9/ref/class-based-views/generic-date-based/#weekarchiveview
    # We will use strftime instead!
    return date.strftime("%W")
