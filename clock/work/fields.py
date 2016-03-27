import datetime

from django.core.exceptions import ValidationError
from django.db.models.fields import IntegerField
from django.db import models
from django.forms.fields import CharField
from django.utils.translation import ugettext_lazy as _

"""
All credit for WorkingHoursFieldForm and WorkingHoursField go to
http://charlesleifer.com/blog/writing-custom-field-django/
and some Google-foo, to understand everything behind it and to make it working
with Django >=1.8.
"""


class WorkingHoursFieldForm(CharField):
    """
    Implementation of a CharField to handle validation of data from WorkingHoursField.

    """
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 5
        super(WorkingHoursFieldForm, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(CharField, self).clean(value)

        # Split submitted duration into list
        hour_value = value.split('.')

        # If list does not have two values, let us do some more validation
        if len(hour_value) != 2:
            # In this case the user did not supply the form with the correct format.
            # Therefore we are going to assume that he does not care about
            # the minutes and we will just append those for him!
            if len(hour_value)<2:
                value = hour_value[0] + ".00"
            # This case should only arise when the format was not correct at all.
            else:
                raise ValidationError(_('Working hours entered must be in format HH.MM'))

        # If the value is in the correct format, check if the total working hours
        # exceed 80 hours per month (this equals 288.000 seconds)
        if len(hour_value) == 2:
            hours, minutes = map(int, value.split('.'))
            total_seconds = hours*3600 + minutes*60
            if total_seconds > 80 * 3600:
                raise ValidationError(_('Contracts may not be longer than 80 hours!'))

        return value


class WorkingHoursField(IntegerField):
    """
    Creates a custom field so we can store our working hours in contracts.
    Working hours are stored as an integer in minutes inside the database.

    This field accepts input in the format HH.MM and will display it the same way.
    """

    # Get values from database and return them as HH.MM
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        hours, minutes = divmod(value, 60)
        return "%02d.%02d" % (hours, minutes)

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, (int, long)):
            return value
        # Split into two values and return the duration in minutes!
        if isinstance(value, basestring):
            hours, minutes = map(int, value.split('.'))
            return (hours * 60) + minutes
        # I do not know if this is really relevant here?
        elif not isinstance(value, datetime.timedelta):
            raise ValidationError('Unable to convert %s to timedelta.' % value)
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        return value

    # This is somehow needed, as otherwise the form will not work correctly!
    def formfield(self, form_class=WorkingHoursFieldForm, **kwargs):
        defaults = {'help_text': _('Please specify your working hours in the format HH:MM \
                                (eg. 12:15 - meaning 12 hours and 15 minutes)')}
        defaults.update(kwargs)
        return form_class(**defaults)
