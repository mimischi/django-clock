# -*- coding: utf-8 -*-
from datetime import datetime

import pytz
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Submit
from dateutil.rrule import DAILY, MONTHLY, WEEKLY, rrule
from django import forms
from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from clock.contracts.models import Contract
from clock.pages.utils import round_time
from clock.shifts.models import Shift
from clock.shifts.utils import get_return_url


class ClockInForm(forms.Form):
    """Form used to clock in the user."""
    started = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS
    )
    contract = forms.ModelChoiceField(
        queryset=Contract.objects.none(),
        empty_label=_('None defined'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if self.fields['contract']:
            self.fields['contract'].queryset = self.user.contract_set.all()

    def clean(self):
        cleaned_data = super().clean()

        if Shift.objects.filter(employee=self.user, finished__isnull=True):
            raise forms.ValidationError(
                _('You cannot clock into two shifts at once!')
            )

        return cleaned_data

    def clock_in(self):
        """Clock in the user."""
        started = self.cleaned_data.get('started')
        contract = self.cleaned_data.get('contract')

        Shift.objects.create(
            started=started, contract=contract, employee=self.user
        )


class ClockOutForm(forms.Form):
    """Clock out the user."""
    finished = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Set a default whether we want to raise a ValidationError if the shift
        # is shorter than five minutes.
        raise_validation = False

        # Chicken out, if we were not passed any Shift instance.
        if self.instance is None:
            raise forms.ValidationError(
                _('You cannot clock out of a non-existent shift!')
            )

        cleaned_data = super().clean()

        # We want to make sure that rounding our datetime objects does not move
        # the `started` value into the next day (edge case if the shift was
        # started on >=23:58). If it does not spill over, we round the time and
        # show the ValidationError if needed.
        if not self.spills_into_next_day(
            self.instance.started, round_time(self.instance.started)
        ):
            raise_validation = True
            self.instance.started = round_time(self.instance.started)

        cleaned_data['finished'] = round_time(cleaned_data['finished'])

        # Check whether the `started` and `finished` datetimes are on different
        # days. If yes, we need to split them into two own objects.
        if self.spills_into_next_day():
            # Save the finished time of the to-be created Shift object.
            new_shift_finished = self.cleaned_data['finished']

            # Set the finished time of the current shift to 23:55 of the
            # current day.
            cleaned_data['finished'] = timezone.make_aware(
                timezone.datetime(
                    self.instance.started.year, self.instance.started.month,
                    self.instance.started.day, 23, 55, 00
                ),
                timezone=pytz.timezone('UTC')
            )

            # Define a starting time for the next day (00:00)
            next_day_started = timezone.make_aware(
                timezone.datetime(
                    new_shift_finished.year, new_shift_finished.month,
                    new_shift_finished.day, 0, 0
                ),
                timezone=pytz.timezone('UTC')
            )
            # Check whether the shift on the new day is actually longer than five minutes.
            # If not, we do not attempt to create it.
            if (new_shift_finished - next_day_started) >= timezone.timedelta(
                minutes=5
            ):
                new_shift = ShiftForm(
                    data={
                        'started': next_day_started,
                        'finished': new_shift_finished,
                        'reoccuring': 'ONCE'
                    },
                    **{
                        'contract': self.instance.contract,
                        'user': self.instance.employee
                    }
                )
                if new_shift.is_valid():
                    new_shift.save()

        # If we came this far, then we were able to process the Shift,
        # splitting of the residual datetime into a new day. We have not yet
        # checked whether the duration on the actual starting day is >= five
        # minutes.
        self.instance.duration = cleaned_data['finished'
                                              ] - self.instance.started

        # Check whether the duration of the Shift object started on the actual
        # day is >= than 5 minutes. Delete otherwise.
        if self.instance.duration < timezone.timedelta(minutes=5):
            Shift.objects.get(pk=self.instance.pk).delete()

            # This is True if the Shift on the current day starts before 23:58.
            # If it is False, it starts just before the day ends and we do not
            # want to show this error.
            if raise_validation:
                # Raise a ValidationError, if the shift is shorter than five minutes.
                raise forms.ValidationError(
                    _(
                        'A shift cannot be shorter than 5 minutes. '
                        'We deleted it for you :)'
                    )
                )

        return cleaned_data

    def spills_into_next_day(self, started=None, finished=None):
        """Returns True if the shift finishes the same day it started."""
        if not started:
            started = self.instance.started
        if not finished:
            finished = self.cleaned_data.get('finished')
        return not (
            (started.year == finished.year) and
            (started.month == finished.month) and
            (started.day == finished.day)
        )

    def clock_out(self):
        """Clock out the user again and update the corresponding fields."""
        shift = Shift.objects.filter(pk=self.instance.pk)
        if shift:
            shift[0].started = self.instance.started
            shift[0].finished = self.cleaned_data.get('finished')
            shift[0].duration = self.instance.duration
            shift[0].save()


REOCCURING_CHOICES = (
    # ('', '---------'),
    ('ONCE', _('Once')),
    ('DAILY', _('Daily')),
    ('WEEKLY', _('Weekly')),
    ('MONTHLY', _('Monthly'))
)
FREQUENCIES = {'DAILY': DAILY, 'WEEKLY': WEEKLY, 'MONTHLY': MONTHLY}


class ShiftForm(forms.ModelForm):
    started = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS
    )

    finished = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS
    )

    reoccuring = forms.ChoiceField(
        choices=REOCCURING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'selectpicker'})
    )

    class Meta:
        model = Shift
        fields = (
            'started',
            'finished',
            'contract',
            'reoccuring',
            'key',
            'tags',
            'note',
        )
        widgets = {
            'contract': forms.Select(attrs={'class': 'selectpicker'}),
            'key': forms.Select(attrs={'class': 'selectpicker'})
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.contract = kwargs.pop('contract')
        self.view = kwargs.pop('view', None)
        self.user = kwargs.pop('user')
        super(ShiftForm, self).__init__(*args, **kwargs)

        if self.view is None:
            self.finished = None
            self.fields['finished'].required = False

            self.contract = None
        else:
            self.fields['contract'].queryset = self.user.contract_set.all()
            self.fields['started'].widget = forms.HiddenInput()
            self.fields['finished'].widget = forms.HiddenInput()

        # Retrieve all contracts that belong to the user
        self.fields['contract'].queryset = Contract.objects.filter(
            employee=self.user
        )

        if not self.fields['contract'].queryset:
            self.fields['contract'].widget.attrs['disabled'] = True

        # Set the delete input to be empty. If we are not on an update page,
        # the button will not be shown!
        delete_html_inject = ""

        # Are we creating a new shift or updating an existing one?
        if self.view == 'shift_create':
            add_input_text = _('Create new shift')
        elif self.view == 'shift_update':
            add_input_text = _('Update')
            delete_html_inject = '<a href="{}" class="{}">{}</a>'.format(
                reverse_lazy('shift:delete', kwargs={'pk': self.instance.pk}),
                'btn btn-danger pull-right second-button', _('Delete')
            )
        else:
            add_input_text = ''

        cancel_html = ''
        if self.request:
            cancel_html = '<a href="{}" class="btn btn-default">{}</a>'.format(
                get_return_url(self.request, 'shift:list'), _('Cancel')
            )

        self.helper = FormHelper(self)
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field(
                'started', template='shift/fields/datetimepicker_field.html'
            ),
            Field(
                'finished', template='shift/fields/datetimepicker_field.html'
            ),
            Field('contract'),
            Field('reoccuring'), Field('key'), Field('tags'), Field('note')
        )
        self.helper.layout.append(
            FormActions(
                HTML(cancel_html),
                Submit(
                    'submit',
                    add_input_text,
                    css_class='btn btn-primary pull-right'
                ),
                HTML(delete_html_inject),
            )
        )

    def clean(self):
        cleaned_data = super().clean()

        self.instance.employee = self.user
        self.started = cleaned_data.get('started')
        self.finished = cleaned_data.get('finished', None)

        # max_shift_duration = timezone.timedelta(minutes=600)

        # First if-case is needed for the quick-action form.
        if self.finished:
            self.instance.duration = self.finished - self.started
        else:
            self.instance.duration = timezone.now() - self.started

        self.time_validation()

        return cleaned_data

    def save(self, commit=True):
        # Perform saving of the super save() method.
        shiftform = super().save(commit=False)

        # Grab the value for the reoccuring field.
        reoccuring = self.cleaned_data.get('reoccuring')

        # Check, if the Shift is reoccuring. If yes, save it several times.
        # Otherwise save it only once.
        if reoccuring != 'ONCE':
            # Populate a dictionary with all values that we need to create new
            # Shifts.
            data = {}
            for field in ['contract', 'key', 'note', 'tags']:
                data[field] = self.cleaned_data.get(field)
            data['duration'] = self.instance.duration
            data['reoccuring'] = 'ONCE'
            started = self.cleaned_data.get('started')
            finished = self.cleaned_data.get('finished')

            # Grab all dates that we need to consider
            dates = list(
                rrule(
                    freq=FREQUENCIES[reoccuring],
                    dtstart=started,
                    until=timezone.make_aware(
                        timezone.datetime(2018, 3, 31),
                        timezone=pytz.timezone('UTC')
                    )
                )
            )

            # TODO: Decide what to do, if we have any collisions.
            for date in dates:
                data['started'] = timezone.datetime(
                    date.year, date.month, date.day, started.hour,
                    started.minute
                )
                data['finished'] = timezone.datetime(
                    date.year, date.month, date.day, finished.hour,
                    finished.minute
                )
                form = ShiftForm(
                    data=data,
                    **{'user': self.user,
                       'contract': data['contract']}
                )
                if form.is_valid():
                    form.save()

        # Check if we want to save the form now.
        if commit:
            shiftform.save()

        return shiftform

    def is_too_long(self, worked_hours=None):
        """Return True/False if the total work time for a given day exceeds ten
        hours.
        """
        if not worked_hours:
            worked_hours = self.work_time_current_day()

        if not self.instance.duration:
            self.instance.duration = timezone.now() - self.started

        return (worked_hours + self.instance.duration) > timezone.timedelta(
            minutes=600
        )

    def work_time_current_day(self):
        """Return the total time worked for a given day."""
        day = self.started.day
        month = self.started.month
        year = self.started.year

        work_time = Shift.objects.filter(
            employee=self.user,
            contract=self.contract,
            started__gte=timezone.make_aware(datetime(year, month, day, 0, 0)),
            finished__lte=timezone.
            make_aware(datetime(year, month, day, 23, 59))
        )
        if self.instance.pk:
            work_time.exclude(pk=self.instance.pk)

        work_time = work_time.aggregate(duration=Sum('duration'))['duration']

        if not work_time:
            work_time = timezone.timedelta(minutes=0)

        return work_time

    def time_validation(self):
        """Validate that the finish time is bigger than the start time.
        """
        if self.finished:
            if self.finished < self.started:
                self.add_error(
                    None, _('The shift cannot start after finishing.')
                )
            elif (self.finished - self.started) < timezone.timedelta(
                minutes=5
            ):
                self.add_error(
                    None, _('We cannot save a shift that is this short.')
                )

        return

    # This could go into models.. at some point? When we create a shift through
    # the shell, no checks will be performed for overlaps!
    def check_for_overlaps(self, employee, started, finished):
        """
        Check if the supplied starting/finishing DateTimes
        overlap with any shifts already present in our database.
        Logic according to: http://stackoverflow.com/a/325964/4791226
        Quick reference: (StartA <= EndB)  and  (EndA >= StartB)
        """
        # TODO: Make this more efficient. We can make the database do all the
        # hard work.
        shifts = Shift.objects.filter(
            employee=employee, started__lte=finished, finished__gte=started
        )

        # Check if the retrieved shifts contain the shift we're trying to
        # update.
        for shift in shifts:
            if shift.pk == self.instance.pk:
                pass
            elif (shift.finished == started) or (shift.started == finished):
                pass
            else:
                return shifts

        return None
