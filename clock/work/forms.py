from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from allauth.account.forms import LoginForm

from clock.work.models import Contract, Shift


class ClockLoginForm(LoginForm):
    text_input = forms.CharField()

    textarea = forms.CharField(
        widget=forms.Textarea(),
    )

    radio_buttons = forms.ChoiceField(
        choices=(
            ('option_one', "Option one is this and that be sure to include why it's great"),
            ('option_two', "Option two can is something else and selecting it will deselect option one")
        ),
        widget=forms.RadioSelect,
        initial='option_two',
    )

    checkboxes = forms.MultipleChoiceField(
        choices=(
            ('option_one', "Option one is this and that be sure to include why it's great"),
            ('option_two', 'Option two can also be checked and included in form results'),
            ('option_three', 'Option three can yes, you guessed it also be checked and included in form results')
        ),
        initial='option_one',
        widget=forms.CheckboxSelectMultiple,
        help_text="<strong>Note:</strong> Labels surround all the options for much larger click areas and a more usable form.",
    )

    appended_text = forms.CharField(
        help_text="Here's more help text"
    )

    prepended_text = forms.CharField()

    prepended_text_two = forms.CharField()

    multicolon_select = forms.MultipleChoiceField(
        choices=(('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')),
    )

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('text_input', css_class='input-xlarge'),
        Field('textarea', rows="3", css_class='input-xlarge'),
        'radio_buttons',
        Field('checkboxes', style="background: #FAFAFA; padding: 10px;"),
        AppendedText('appended_text', '.00'),
        PrependedText('prepended_text', '<input type="checkbox" checked="checked" value="" id="" name="">',
                      active=True),
        PrependedText('prepended_text_two', '@'),
        'multicolon_select',
        FormActions(
            Submit('save_changes', 'Save changes', css_class="btn-primary"),
            Submit('cancel', 'Cancel'),
        )
    )


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
                    "stepping": 5,
                    "toolbarPlacement": "top",
                    "calendarWeeks": True
                }
            ),
            'shift_finished': DateTimePicker(
                options={
                    "format": "YYYY-MM-DD HH:mm",
                    "stepping": 5,
                    "toolbarPlacement": "top",
                    "calendarWeeks": True
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

            # So if we are updating an already existing entry, we may also set some restrictions on the DateTimePicker
            # The shift_finished picker can't be set BEFORE the shift_started datetime. Updating either of both
            # will update the restriction dynamically via JavaScript.
            self.fields.update({
                'shift_finished': forms.DateTimeField(
                    widget=DateTimePicker(
                        options={
                            "format": "YYYY-MM-DD HH:mm",
                            "stepping": 5,
                            "toolbarPlacement": "top",
                            "calendarWeeks": False,
                            "minDate": unicode(self.initial['shift_started'].strftime("%Y-%m-%d %H:%M"))
                        }
                    ),
                ),
                # This one does not seem to work, so we disable it.
                # Enabling it will set the shift_started field to the same value as the shift_finished..
                # This seems to be caused by the embedded JavaScript, as the replacement happens after a full page load.

                'shift_started': forms.DateTimeField(
                    widget=DateTimePicker(
                        options={
                            "format": "YYYY-MM-DD HH:mm",
                            "stepping": 5,
                            "toolbarPlacement": "top",
                            "calendarWeeks": False,
                            # "maxDate": unicode(self.initial['shift_finished'].strftime("%Y-%m-%d %H:%M"))
                        }
                    ),
                ),
            })

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

    # This could go into models.. at some point? When we create a shift through
    # the shell, no checks will be performed for overlaps!
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
