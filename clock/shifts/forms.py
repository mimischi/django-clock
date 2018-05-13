# -*- coding: utf-8 -*-
from datetime import datetime

import pytz
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Submit
from dateutil.rrule import DAILY, MONTHLY, WEEKLY, rrule
from django import forms
from django.conf import settings
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
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
            next_day_finished = self.cleaned_data['finished']

            # Check whether the new shift will finish tomorrow or later.
            # If it is some day after tomorrow, we set it to tomorrow 23:55.
            year = self.instance.started.year
            month = self.instance.started.month
            day = self.instance.started.day
            started_date = timezone.datetime(year, month, day)
            reference_next_day = timezone.make_aware(
                datetime.combine(started_date, datetime.max.time())
            ) + timezone.timedelta(days=1)

            if next_day_finished > reference_next_day:
                next_day_finished = timezone.make_aware(
                    timezone.datetime(
                        reference_next_day.year, reference_next_day.month,
                        reference_next_day.day, 23, 55
                    )
                )

            # Set the finished time of the current shift to 23:55 of the
            # current day.
            cleaned_data['finished'] = timezone.make_aware(
                timezone.datetime(
                    self.instance.started.year, self.instance.started.month,
                    self.instance.started.day, 23, 55, 00
                )
            ).astimezone(pytz.utc)

            # Define a starting time for the next day (00:00)
            next_day_started = timezone.make_aware(
                timezone.datetime(
                    next_day_finished.year, next_day_finished.month,
                    next_day_finished.day, 0, 0
                )
            )
            # Check whether the shift on the new day is actually longer than
            # five minutes. If not, we do not attempt to create it.
            next_day_duration = next_day_finished - next_day_started
            if next_day_duration >= timezone.timedelta(minutes=5):
                new_shift = ShiftForm(
                    data={
                        'started': next_day_started,
                        'finished': next_day_finished,
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
                # Raise a ValidationError, if the shift is shorter than five
                # minutes.
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

    end_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = Shift
        fields = (
            'started',
            'finished',
            'contract',
            'reoccuring',
            'end_date',
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
        self.contract = kwargs.pop('contract', None)
        self.view = kwargs.pop('view', None)
        self.user = kwargs.pop('user')
        super(ShiftForm, self).__init__(*args, **kwargs)

        for field_to_hide in ['end_date']:
            self.fields[field_to_hide].required = False
            self.fields[field_to_hide].widget = forms.HiddenInput()

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
        self.helper.attrs = {'name': 'shiftForm'}
        self.helper.form_id = 'shiftForm'
        self.helper.layout = Layout(
            Field(
                'started', template='shift/fields/datetimepicker_field.html'
            ),
            Field(
                'finished', template='shift/fields/datetimepicker_field.html'
            ), Field('contract'), Field('reoccuring'),
            Field(
                'end_date', template='shift/fields/datetimepicker_field.html'
            ), Field('key'), Field('tags'), Field('note')
        )
        self.helper.layout.append(
            FormActions(
                HTML(cancel_html),
                Submit(
                    'submitShiftForm',
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
        self.finished = cleaned_data.get('finished')
        self.instance.duration = self.finished - self.started

        # Do not allow a manually created Shift to spill into the next day.
        if not (
            (self.started.year == self.finished.year) and
            (self.started.month == self.finished.month) and
            (self.started.day == self.finished.day)
        ):
            self.add_error(
                'finished', _('A shift can never end on the next day.')
            )

        reoccuring = self.cleaned_data.get('reoccuring')
        if reoccuring != 'ONCE' and self.cleaned_data.get(
            'contract'
        ) and self.cleaned_data.get('contract').end_date and (
            self.cleaned_data.get('end_date') >
            self.cleaned_data.get('contract').end_date
        ):
            self.add_error(
                'end_date',
                _('You cannot plan shifts after the end of a contract.')
            )

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
            contract = self.cleaned_data.get('contract', None)
            if contract is not None:
                contract = contract.pk

            data = {}
            for field in ['key', 'note', 'tags', 'end_date']:
                data[field] = self.cleaned_data.get(field)
            data['contract'] = contract
            data['duration'] = self.instance.duration
            data['reoccuring'] = 'ONCE'
            started = self.cleaned_data.get('started')
            finished = self.cleaned_data.get('finished')

            # Grab all dates that we need to consider
            end_date_datetime = datetime.combine(
                data['end_date'], datetime.min.time()
            )
            dates = list(
                rrule(
                    freq=FREQUENCIES[reoccuring],
                    dtstart=started,
                    until=end_date_datetime.astimezone(pytz.utc)
                )
            )

            for date in dates[1:]:
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
                    **{
                        'user': self.user,
                        'contract': data['contract']
                    }
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

        return (worked_hours +
                self.instance.duration) > timezone.timedelta(minutes=600)

    def work_time_current_day(self):
        """Return the total time worked for a given day."""
        day = self.started.day
        month = self.started.month
        year = self.started.year

        work_time = Shift.objects.filter(
            employee=self.user,
            contract=self.contract,
            started__gte=timezone.make_aware(datetime(year, month, day, 0, 0)),
            finished__lte=timezone.make_aware(
                datetime(year, month, day, 23, 59)
            )
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

        if not self.finished:
            return

        if self.finished < self.started:
            self.add_error(None, _('The shift cannot start after finishing.'))
        elif (self.finished - self.started) < timezone.timedelta(minutes=5):
            self.add_error(
                None, _('We cannot save a shift that is this short.')
            )

        overlaps = self.check_for_overlaps
        if not overlaps:
            return

        shift_word = 'shifts' if len(overlaps) > 1 else 'shift'

        self.add_error(
            None,
            _(
                'The current shift overlaps with the '
                'following saved {}:'.format(shift_word)
            )
        )
        for shift in overlaps:
            started = timezone.localtime(shift.started
                                         ).strftime("%d.%m.%Y %H:%M")
            finished = timezone.localtime(shift.finished
                                          ).strftime("%d.%m.%Y %H:%M")
            duration = shift.duration
            days, seconds = duration.days, duration.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            duration = "{:02}:{:02}".format(hours, minutes)

            error_string = '<a href="{}"><strong>Contract:</strong> {}; ' \
                           '<strong>Started:</strong> {}; ' \
                           '<strong>Duration:</strong> {}; ' \
                           '<strong>Finished:</strong> {}</a>'.format(
                               reverse_lazy('shift:edit', args=[shift.pk]),
                               shift.contract, started, duration, finished
                           )
            self.add_error(None, mark_safe(_(error_string)))

    @property
    def check_for_overlaps(self):
        """Check if the supplied starting/finishing DateTimes
        overlap with any shifts already present in our database.

        We only check this if the current Shift belongs to some contract.
        Further we ignore all Shifts that do not belong to any contract.

        We want Shifts to be able to begin and end on the same minute.
        Therefore we are using < and > instead of <= and >=.

        Logic according to: http://stackoverflow.com/a/325964/4791226
        Quick reference: (StartA < EndB) and (EndA > StartB)
        """
        shifts = None

        # Only perform the check if the current Shift belongs to some contract
        contract = self.cleaned_data.get('contract', None)
        if contract is not None:
            shifts = Shift.objects.filter(
                employee=self.instance.employee,
                started__lt=self.finished,
                finished__gt=self.started,
                contract__isnull=False    # Ignore Shifts without contracts
            ).exclude(pk=self.instance.pk)

        return shifts

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
