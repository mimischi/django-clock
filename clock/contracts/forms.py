# -*- coding: utf-8 -*-
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from clock.contracts.models import Contract


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ('department', 'department_short', 'hours',)
        # This could be used to select working hours with a widget. Right now it does not support values above 24 hours
        # widgets = {
        #     'hours': DateTimePicker(
        #         options={
        #             "format": "HH.mm",
        #             "stepping": 10,
        #             "toolbarPlacement": "top",
        #             "maxDate": 80,
        #         }
        #     ),
        # }

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
            delete_html_inject = u'<a href="%(delete_url)s" class="btn btn-danger pull-right second-button"> \
            %(delete_translation)s</a>' % {'delete_url': reverse_lazy('contract:delete',
                                                                      kwargs={
                                                                          'pk': self.instance.pk}),
                                           'delete_translation': _('Delete')}

        cancel_html_inject = '<a href="%(cancel_url)s" class="btn btn-default">%(cancel_translation)s</a>' % \
                             {'cancel_url': reverse_lazy('contract:list'), 'cancel_translation': _('Cancel')}

        self.helper = FormHelper(self)
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.layout.append(FormActions(
            HTML(cancel_html_inject),
            Submit('submit', add_input_text, css_class='btn btn-primary pull-right'),
            HTML(delete_html_inject),
        ))
