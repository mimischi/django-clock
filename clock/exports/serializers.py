from datetime import datetime, timedelta

from django.core.serializers.json import DjangoJSONEncoder

from clock.pages.templatetags.format_duration import format_dttd


class ShiftJSONEncoder(DjangoJSONEncoder):
    """
    A custom JSONEncoder extending `DjangoJSONEncoder` to handle serialization
    of Shift data.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            r = obj.isoformat(' ')
            if obj.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(obj, timedelta):
            return format_dttd(obj, "%H:%M")
        elif obj is None:
            return "None"
        else:
            return super(DjangoJSONEncoder, self).default(obj)
