from django import template
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
