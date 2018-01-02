# -*- coding: utf-8 -*-
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from clock.contracts.models import Contract
from clock.shifts.models import Shift
from clock.shifts.utils import get_return_url


class QuickActionForm(forms.Form):
    """
    Small helper form for the selection of an institute/contract
    on the dashboard for the quick buttons.
    """

    contract = forms.ModelChoiceField(
        queryset=Contract.objects.none(), empty_label=_('None defined'))

    def __init__(self, *args, **kwargs):
        # Retrieve the logged in user, that we provide inside the view
        self.user = kwargs.pop('user', None)
        super(QuickActionForm, self).__init__(*args, **kwargs)
        # Only show the users contracts
        self.fields['contract'].queryset = self.user.contract_set.all()


class ShiftForm(forms.ModelForm):
    started = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS)
    finished = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS)

    class Meta:
        model = Shift
        fields = (
            'started',
            'finished',
            'pause_duration',
            'contract',
            'key',
            'tags',
            'note', )
        widgets = {
            'contract': forms.Select(attrs={'class': 'selectpicker'}),
            'key': forms.Select(attrs={'class': 'selectpicker'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.contract = kwargs.pop('contract')
        self.view = kwargs.pop('view')
        self.user = self.request.user
        super(ShiftForm, self).__init__(*args, **kwargs)

        self.fields['started'].widget = forms.HiddenInput()
        self.fields['finished'].widget = forms.HiddenInput()
        self.fields['pause_duration'].widget = forms.HiddenInput()

        # Retrieve all contracts that belong to the user
        self.fields['contract'].queryset = Contract.objects.filter(
            employee=self.user)

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
                'btn btn-danger pull-right second-button', _('Delete'))

        cancel_html = '<a href="{}" class="btn btn-default">{}</a>'.format(
            get_return_url(self.request, 'shift:list'), _('Cancel'))

        self.helper = FormHelper(self)
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field(
                'started', template='shift/fields/datetimepicker_field.html'),
            Field(
                'finished', template='shift/fields/datetimepicker_field.html'),
            Field(
                'pause_duration',
                template='shift/fields/datetimepicker_field.html'),
            Field('contract'), Field('key'), Field('tags'), Field('note'))
        self.helper.layout.append(
            FormActions(
                HTML(cancel_html),
                Submit(
                    'submit',
                    add_input_text,
                    css_class='btn btn-primary pull-right'),
                HTML(delete_html_inject), ))

    def clean_pause_duration(self):
        pause_duration = self.cleaned_data.get('pause_duration')
        return pause_duration * 60

    def clean(self):
        cleaned_data = super(ShiftForm, self).clean()

        employee = self.user
        started = cleaned_data.get('started')
        finished = cleaned_data.get('finished')
        pause_duration = cleaned_data.get('pause_duration')

        # If both values were entered into the form,
        # check if they overlap with any other shifts
        if finished and started:
            check_for_overlaps = self.check_for_overlaps(
                employee, started, finished)
            if check_for_overlaps:
                raise ValidationError(
                    _('Your selected starting/finishing time overlaps with at '
                      'least one finished shift of yours. '
                      'Please adjust the times.'))

            if (finished - started) < pause_duration:
                raise ValidationError(
                    _('A pause may not be longer than your actual shift.'))

        cleaned_data['bool_finished'] = True

        return cleaned_data

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
            employee=employee, started__lte=finished, finished__gte=started)

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
