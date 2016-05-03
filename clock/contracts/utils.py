from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def convert_work_hours(work_hours):
    try:
        hours, minutes = map(int, work_hours.split('.'))
    except ValueError:
        raise ValidationError(_('Could not split the value during one internal function (convert_work_hours).'))
    return (hours*60) + minutes
