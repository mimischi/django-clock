from django.core.exceptions import ValidationError


def convert_work_hours(work_hours):
    try:
        hours, minutes = map(int, work_hours.split(':'))
    except ValueError:
        raise ValidationError('Could not split the value during one internal function (convert_work_hours).')
    return (hours*60) + minutes
