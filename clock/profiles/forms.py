# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from clock.users.models import User


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', )

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id=updateUserForm'
        self.helper.form_method = 'post'
        self.helper.form_action = ''

        self.helper.add_input(Submit('submit', _('Update')))

    def clean(self):
        super(UpdateUserForm, self).clean()

        if self.cleaned_data['first_name'] and not self.cleaned_data['last_name'] \
           or not self.cleaned_data['first_name'] and self.cleaned_data['last_name']:
            raise ValidationError(
                _('When specifying your real name, you must give both your first and last name.'
                  ))


class DeleteUserForm(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        max_length=80,
        required=True, )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(DeleteUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-deleteUserForm'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'

        self.helper.add_input(Submit('submit', _('Delete')))

    def clean_username(self):
        if self.cleaned_data['username'] != self.user.username:
            raise ValidationError(_('The input does not match your username!'))

        return self.cleaned_data['username']
