from django import template
from time import strftime
# from datetime import timedelta

register = template.Library()


@register.filter
def format_timedelta(td):
    minutes, seconds = divmod(td.seconds + td.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)


@register.filter
def format_timedelta2(td):
    minutes, seconds = divmod(td.seconds + td.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}'.format(hours, minutes)

    # Returns the time without the microseconds
    # time = td - timedelta(microseconds=td.microseconds)
    # return time


# Django docs says we should not use built-in |date template filter to display week numbers.
# See: https://docs.djangoproject.com/en/1.9/ref/class-based-views/generic-date-based/#weekarchiveview
# We will use strftime instead!
@register.filter
def format_week(date):
    return date.strftime("%W")
