# -*- coding: utf-8 -*-
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Submit
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from clock.contracts.models import Contract


class ContractForm(forms.ModelForm):
    show_start_end_date = forms.BooleanField()
    start_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    end_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = Contract
        fields = (
            "department",
            "start_date",
            "show_start_end_date",
            "end_date",
            "hours",
        )

    def __init__(self, *args, **kwargs):
        # Grab kwargs provided by the view
        self.view = kwargs.pop("view", None)
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["start_date"].widget = forms.HiddenInput()
        self.fields["end_date"].widget = forms.HiddenInput()
        self.fields["start_date"].required = False
        self.fields["end_date"].required = False
        self.fields["show_start_end_date"].required = False

        delete_html_inject = ""
        add_input_text = ""

        # Determine if we're creating a new shift or updating an existing one
        if self.view == "create":
            add_input_text = _("Create new contract")
        elif self.view == "update":
            add_input_text = _("Update contract")
            delete_html_inject = '<a href="{}" class="{}">{}</a>'.format(
                reverse_lazy("contract:delete", kwargs={"pk": self.instance.pk}),
                "btn btn-danger pull-right second-button",
                _("Delete"),
            )

        cancel_html_inject = '<a href="{}" class="{}">{}</a>'.format(
            reverse_lazy("contract:list"), "btn btn-default", _("Cancel")
        )

        self.helper = FormHelper(self)
        self.helper.form_action = "."
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("department"),
            Field("hours"),
            Field("show_start_end_date"),
            Field("start_date", template="shift/fields/datetimepicker_field.html"),
            Field("end_date", template="shift/fields/datetimepicker_field.html"),
        )
        self.helper.layout.append(
            FormActions(
                HTML(cancel_html_inject),
                Submit(
                    "submit", add_input_text, css_class="btn btn-primary pull-right"
                ),
                HTML(delete_html_inject),
            )
        )

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)

        start = self.cleaned_data["start_date"]
        end = self.cleaned_data["end_date"]

        if start and not end:
            self.add_error("end_date", "")
            raise forms.ValidationError(
                _("You need to specify an end date for the contract.")
            )

        if end and not start:
            self.add_error("start_date", "")
            raise forms.ValidationError(
                _("You need to specify a start date for the contract.")
            )

        if (start and end) and (end <= start):
            self.add_error("start_date", "")
            self.add_error("end_date", "")
            raise forms.ValidationError(
                _("The end date must be bigger than the start date.")
            )
