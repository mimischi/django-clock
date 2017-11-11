import datetime

from django.core.exceptions import ValidationError
from django.db.models.fields import IntegerField
from django.forms.fields import CharField
from django.utils.translation import ugettext_lazy as _


"""
All credit for WorkingHoursFieldForm and WorkingHoursField go to
http://charlesleifer.com/blog/writing-custom-field-django/
and some Google-foo, to understand everything behind it and to make it work
with Django >=1.8.
"""


class WorkingHoursFieldForm(CharField):
    """Implementation of a CharField to handle validation of data from
    WorkingHoursField.
    """

    def __init__(self, label=_('Work hours'), *args, **kwargs):
        kwargs['max_length'] = 5
        super(WorkingHoursFieldForm, self).__init__(
            label=label, *args, **kwargs)

    def clean(self, value):
        """Checks the supplied data from the users. Accepts work hours in the format
        of "HH:MM" (e.g. 14:35) Needs to check two cases:

            a) Did the user supply the correct format (HH:MM)?

            b) If this fails, then we'll try to assume the user only entered
            the hours (HH) and we'll add the minutes by ourselves. This will
            also check if the entered value is actually an int!

        Furthermore check if the total work time is bigger than zero and
        smaller than 80 hours (288.000 seconds)
        """
        value = super(CharField, self).clean(value)

        try:
            hours, minutes = map(int, value.split(':'))
        except ValueError:
            try:
                hours = int(value)
                value = value + ":00"
                minutes = 0
            except ValueError:
                raise ValidationError(
                    _('Working hours entered must be in format HH:MM'))

        # If the value is in the correct format, check if the total working
        # hours exceed 80 hours per month (this equals 288.000 seconds)
        total_seconds = hours * 3600 + minutes * 60
        if total_seconds > 80 * 3600:
            raise ValidationError(
                _('Contracts may not be longer than 80 hours!'))
        elif total_seconds < 1:
            raise ValidationError(
                _('Your total work time must be bigger than zero!'))

        return value


class WorkingHoursField(IntegerField):
    """Creates a custom field so we can store our working hours in contracts.
    Working hours are stored as an integer in minutes inside the database.

    This field accepts input in the format HH.MM and will display it the same
    way.
    """

    # Get values from database and return them as HH.MM
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        hours, minutes = divmod(value, 60)
        return "%02d:%02d" % (hours, minutes)

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, int):
            return value
        # Split into two values and return the duration in minutes!
        if isinstance(value, str):
            try:
                hours, minutes = map(int, value.split(':'))
            except ValueError:
                raise ValidationError(
                    _('Working hours entered must be in format HH:MM'))

            # If the user entered a value like '30.3' we will convert it into
            # '30.30'. Otherwise it would be interpreted as '30.03'.
            if len(value.split(':')[1]) == 1 and minutes < 10:
                minutes *= 10
            return (hours * 60) + minutes
        # I do not know if this is really relevant here?
        elif not isinstance(value, datetime.timedelta):
            raise ValidationError('Unable to convert %s to timedelta.' % value)
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        return value

    # This is somehow needed, as otherwise the form will not work correctly!
    def formfield(self, form_class=WorkingHoursFieldForm, **kwargs):
        defaults = {
            'help_text':
            _('Please specify your working hours in the format HH:MM '
              '(eg. 12:15 - meaning 12 hours and 15 minutes)')
        }
        defaults.update(kwargs)
        return form_class(**defaults)
