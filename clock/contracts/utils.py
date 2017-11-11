from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def convert_work_hours(work_hours):
    try:
        hours, minutes = list(map(int, work_hours.split(':')))
    except ValueError:
        raise ValidationError(_('Could not split the value you provided.'))
    return (hours * 60) + minutes
