from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Field, Submit
from clock.work.models import Contract, Shift


class ContractFilterform(forms.Form):
    start_date = forms.DateField()
    finish_date = forms.DateField()


class QuickActionForm(forms.Form):
    """
    Small helper form for the selection of an institute/contract
    on the dashboard for the quick buttons.
    """

    contract = forms.ModelChoiceField(
        queryset=Contract.objects.none(),
        empty_label=_('None defined')
        )

    def __init__(self, *args, **kwargs):
        # Retrieve the logged in user, that we provide inside the view
        self.user = kwargs.pop('user', None)
        super(QuickActionForm, self).__init__(*args, **kwargs)
        # Only show the users contracts
        self.fields['contract'].queryset = self.user.contract_set.all()


class ContractForm(forms.ModelForm):

    class Meta:
        model = Contract
        fields = ('department', 'department_short', 'hours',)
        # widgets = {
        #     'hours': forms.TextInput(
        #                             attrs={'type': 'number', 'step': '0.15'}
        #             )
        #     }

    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)

        # Retrieve current user, supplied by the view
        self.requested_user = self.initial['user']

        # Determine if we're creating a new shift or updating an existing one
        if self.initial['view'] == 'contract_create':
            add_input_text = _('Create new contract')
        elif self.initial['view'] == 'contract_update':
            add_input_text = _('Update contract')

        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.add_input(
                              Submit('submit',
                                     add_input_text,
                                     css_class='btn btn-primary pull-right')
                              )


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ('shift_started', 'shift_finished', 'pause_duration', 'contract', 'note',)
        widgets = {
            'shift_started': DateTimePicker(
                options={
                    "format": "YYYY-MM-DD HH:mm",
                    "locale": "de",
                    "stepping": 5,
                    "toolbarPlacement": "top",
                }
            ),
            'shift_finished': DateTimePicker(
                options={
                    "format": "YYYY-MM-DD HH:mm",
                    "locale": "de",
                    "stepping": 5,
                    "toolbarPlacement": "top",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(ShiftForm, self).__init__(*args, **kwargs)

        # Retrieve current user, supplied by the view
        self.requested_user = self.initial['user']

        # Retrieve all contracts that belong to the user
        self.fields['contract'].queryset = Contract.objects.filter(
            employee=self.requested_user
        )

        # Are we creating a new shift or updating an existing one?
        if self.initial['view'] == 'shift_create':
            add_input_text = _('Create new shift')
        elif self.initial['view'] == 'shift_update':
            add_input_text = _('Update shift')

        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit(
                                     'submit',
                                     add_input_text,
                                     css_class='btn btn-primary pull-right')
                              )

    def clean(self):
        cleaned_data = super(ShiftForm, self).clean()

        employee = self.requested_user
        shift_started = cleaned_data.get('shift_started')
        shift_finished = cleaned_data.get('shift_finished')

        # If both values were entered into the form,
        # check if they overlap with any other shifts
        if shift_finished and shift_started:
            check_for_overlaps = self.check_for_overlaps(
                                    employee,
                                    shift_started,
                                    shift_finished
                                )
            if check_for_overlaps:
                raise ValidationError(
                    _('Your selected starting/finishing time overlaps with at least one\
                     finished shift of yours. Please adjust the times.'))

        return cleaned_data

    def check_for_overlaps(self, employee, shift_started, shift_finished):
        """
        Check if the supplied starting/finishing DateTimes
        overlap with any shifts already present in our database.
        Logic according to: http://stackoverflow.com/a/325964/4791226
        Quick reference: (StartA <= EndB)  and  (EndA >= StartB)
        """
        shifts = Shift.objects.filter(
                                      employee=employee,
                                      shift_started__lte=shift_finished,
                                      shift_finished__gte=shift_started
                                      )

        # Check if the retrieved shifts contain the shift we're trying to update. If yes: pass.
        for shift in shifts:
            if shift == self.instance:
                pass
            else:
                return shifts

        return None
