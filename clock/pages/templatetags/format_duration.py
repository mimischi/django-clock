import time
from datetime import datetime, timedelta

from django import template

register = template.Library()


@register.filter()
def format_dttd(t, t_format="%H:%M:%S"):
    """
    Should be used to format a given datetime or timedelta (hence dttd) to a specific format.
    :param t: Datetime or timedelta object
    :param t_format: Format the object should be returned as (e.g. "%H:%M" for 23:15)
    :return: Returns string of the formatted dt/td object
    """
    if isinstance(t, timedelta):
        return time.strftime(t_format, time.gmtime(t.seconds + t.days * 86400))
    if isinstance(t, datetime):
        return t.strftime(t_format)
    raise ValueError('The provided object %s does not match any accepted classes.' % t)


@register.filter
def format_week(date):
    # Django docs says we should not use built-in |date template filter to display week numbers.
    # See: https://docs.djangoproject.com/en/1.9/ref/class-based-views/generic-date-based/#weekarchiveview
    # We will use strftime instead!
    return date.strftime("%W")
