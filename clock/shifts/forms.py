# -*- coding: utf-8 -*-
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.forms import DateTimeField
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
    shift_started = DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS)
    shift_finished = DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS)

    class Meta:
        model = Shift
        fields = (
            'shift_started',
            'shift_finished',
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
        # self.fields['shift_started'].widget = forms.HiddenInput()

        # Retrieve all contracts that belong to the user
        self.fields['contract'].queryset = Contract.objects.filter(
            employee=self.user)

        if not self.fields['contract'].queryset:
            self.fields['contract'].widget.attrs['disabled'] = True

        # Set the delete input to be empty. If we are not on an update page, the button will not be shown!
        delete_html_inject = ""

        # Are we creating a new shift or updating an existing one?
        if self.view == 'shift_create':
            add_input_text = _('Create new shift')
        elif self.view == 'shift_update':
            add_input_text = _('Update')
            delete_html_inject = u'<a href="%(delete_url)s" class="btn btn-danger pull-right second-button"> \
                                %(delete_translation)s</a>' % {
                'delete_url':
                reverse_lazy('shift:delete', kwargs={'pk': self.instance.pk}),
                'delete_translation':
                _('Delete')
            }

        cancel_html_inject = '<a href="%(cancel_url)s" class="btn btn-default">%(cancel_translation)s</a>' % \
                             {'cancel_url': get_return_url(self.request, 'shift:list'),
                              'cancel_translation': _('Cancel')}

        self.helper = FormHelper(self)
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.layout.append(
            FormActions(
                HTML(cancel_html_inject),
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
        shift_started = cleaned_data.get('shift_started')
        shift_finished = cleaned_data.get('shift_finished')
        pause_duration = cleaned_data.get('pause_duration')

        # If both values were entered into the form,
        # check if they overlap with any other shifts
        if shift_finished and shift_started:
            check_for_overlaps = self.check_for_overlaps(
                employee, shift_started, shift_finished)
            if check_for_overlaps:
                raise ValidationError(
                    _('Your selected starting/finishing time overlaps with at least one\
                     finished shift of yours. Please adjust the times.'))

            if (shift_finished - shift_started) < pause_duration:
                raise ValidationError(
                    _('A pause may not be longer than your actual shift.'))

        cleaned_data['bool_finished'] = True

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
            shift_finished__gte=shift_started)

        # Check if the retrieved shifts contain the shift we're trying to update. If yes: pass.
        for shift in shifts:
            if shift.pk == self.instance.pk:
                pass
            elif shift.shift_finished == shift_started or shift.shift_started == shift_finished:
                pass
            else:
                return shifts

        return None
