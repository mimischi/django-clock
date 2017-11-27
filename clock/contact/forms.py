# -*- coding: utf-8 -*-
from captcha.fields import ReCaptchaField
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language


class ContactForm(forms.Form):
    name = forms.CharField(max_length=200, label=_('Name'))
    sender = forms.EmailField(label=_('E-Mail'))
    message = forms.CharField(widget=forms.Textarea, label=_('Message'))
    cc_myself = forms.BooleanField(
        label=_('Send a copy of the mail to myself'), required=False)
    captcha = ReCaptchaField(attrs={'lang': get_language()})

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-halfpage'
        self.helper.layout.append(
            FormActions(
                Submit(
                    'submit',
                    _('Submit'),
                    css_class='btn btn-primary pull-right'), ))

    def send_mail(self, form):
        message = form.cleaned_data['message']
        sender = form.cleaned_data['sender']
        cc_myself = form.cleaned_data['cc_myself']

        recipients = settings.CONTACT_FORM_RECIPIENT
        if cc_myself:
            recipients.append(sender)

        send_mail(settings.CONTACT_FORM_SUBJECT, message, sender, recipients)
        return HttpResponseRedirect('/thanks/')
