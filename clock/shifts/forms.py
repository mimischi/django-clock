# -*- coding: utf-8 -*-
from datetime import datetime

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Submit
from django import forms
from django.conf import settings
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
        cleaned_data = super().clean()

        if self.instance is None:
            raise forms.ValidationError(
                _('You cannot clock out of a non-existent shift!')
            )
        # Round times to nearest five minutes when finishing the shift
        self.instance.started = round_time(self.instance.started)
        cleaned_data['finished'] = round_time(cleaned_data['finished'])

        self.instance.duration = cleaned_data['finished'
                                              ] - self.instance.started

        # Raise a ValidationError, if the shift is shorter than five minutes.
        if self.instance.duration < timezone.timedelta(minutes=5):
            shift = self.get_shift(pk=self.instance.pk)
            shift.delete()
            raise forms.ValidationError(
                _(
                    'A shift cannot be shorter than 5 minutes. We deleted it for you :)'
                )
            )

        return cleaned_data

    def get_shift(self, pk):
        """Access the current shift object."""
        return Shift.objects.get(pk=pk)

    def clock_out(self):
        """Clock out the user again and update the corresponding fields."""
        shift = self.get_shift(pk=self.instance.pk)
        shift.started = self.instance.started
        shift.finished = self.cleaned_data.get('finished')
        shift.duration = self.instance.duration
        shift.save()


class ShiftForm(forms.ModelForm):
    started = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS
    )

    finished = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS
    )

    # contract = forms.ModelChoiceField(
    #     queryset=Contract.objects.none(), empty_label=_('None defined')
    # )

    class Meta:
        model = Shift
        fields = (
            'started',
            'finished',
            'contract',
            'key',
            'tags',
            'note',
        )
        widgets = {
            'contract': forms.Select(attrs={'class': 'selectpicker'}),
            'key': forms.Select(attrs={'class': 'selectpicker'}),
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

        # TODO: We can probably remove this again
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
            ), Field('contract'), Field('key'), Field('tags'), Field('note')
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
        self.cleaned_data = super().clean()

        self.instance.employee = self.user
        self.started = self.cleaned_data.get('started')
        self.finished = self.cleaned_data.get('finished', None)
        # max_shift_duration = timezone.timedelta(minutes=600)

        # First if-case is needed for the quick-action form.
        if self.finished:
            self.instance.duration = self.finished - self.started
        else:
            self.instance.duration = timezone.now() - self.started

        # Cache the work time a user has completed for today
        work_time = self.work_time_current_day()
        # Proceed if the work time does not exceed the maximal duration for
        # today.
        # if work_time >= max_shift_duration:
        #     raise ValidationError(
        #         _('You cannot work more than ten hours a day!'),
        #         code='invalid'
        #     )
        # else:
        #     self.started = timezone.now()

        #     if not self.contract:
        #         self.contract = None

        # TODO: Remove this? We actually do not want to force such limits on the user.
        # Limit the current shift to the residual time there is left
        # for the day.
        # if (self.instance.duration + work_time) > max_shift_duration:
        #     self.finished = self.started + (max_shift_duration - work_time)
        #     self.instance.duration = self.finished - self.started
        #     self.cleaned_data['finished'] = self.finished
        #     raise ValidationError('YOYOOYOY')

        self.time_validation()

        # Check for overlaps
        # check_for_overlaps = self.check_for_overlaps(
        #     self.employee, self.started, self.finished
        # )
        # if check_for_overlaps:
        #     raise ValidationError(
        #         _(
        #             'Your selected starting/finishing time overlaps with '
        #             'at least one finished shift of yours. '
        #             'Please adjust the times.'
        #         )
        #     )

        return self.cleaned_data

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
