# -*- coding: utf-8 -*-
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Submit
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from clock.contracts.models import Contract


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = (
            'department',
            'department_short',
            'hours', )

    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)

        # Retrieve current user, supplied by the view
        self.requested_user = self.initial['user']

        delete_html_inject = ""

        # Determine if we're creating a new shift or updating an existing one
        if self.initial['view'] == 'contract_create':
            add_input_text = _('Create new contract')
        elif self.initial['view'] == 'contract_update':
            add_input_text = _('Update contract')
            delete_html_inject = '<a href="{}" class="{}">{}</a>'.format(
                reverse_lazy(
                    'contract:delete', kwargs={'pk': self.instance.pk}),
                'btn btn-danger pull-right second-button', _('Delete'))

        cancel_html_inject = '<a href="{}" class="{}">{}</a>'.format(
            reverse_lazy('contract:list'), 'btn btn-default', _('Cancel'))

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
