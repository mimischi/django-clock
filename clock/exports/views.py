# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from braces.views import JSONResponseMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.dates import MonthArchiveView

from clock.contracts.models import Contract
from clock.exports.mixins import PdfResponseMixin
from clock.exports.serializers import ShiftJSONEncoder
from clock.shifts.models import Shift


@method_decorator(login_required, name="dispatch")
class ExportMonth(PdfResponseMixin, MonthArchiveView):
    model = Shift
    date_field = "shift_started"
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super(ExportMonth, self).get_context_data(**kwargs)

        # TODO: Can result in text overflowing the drawn box!
        context['fullname'] = '{} {}'.format(self.request.user.first_name,
                                             self.request.user.last_name)

        if not context['shift_list']:
            context['department'] = Contract.objects.get(
                pk=int(self.kwargs['pk'])).department
            context['total_shift_duration'] = timedelta(seconds=0)
        else:
            context['department'] = context['shift_list'][0].contract_or_none

        total_shift_duration = timedelta(seconds=0)
        for shift in context['shift_list']:
            total_shift_duration += shift.shift_duration
            context['total_shift_duration'] = total_shift_duration
        return context

    def get_queryset(self):
        contract_pk = self.kwargs['pk']
        return Shift.objects.filter(
            employee=self.request.user.pk,
            contract=contract_pk,
            shift_finished__isnull=False)


@method_decorator(login_required, name="dispatch")
class ExportMonthClass(JSONResponseMixin, MonthArchiveView):
    model = Shift
    date_field = "shift_started"
    json_dumps_kwargs = {u"indent": 2}
    json_encoder_class = ShiftJSONEncoder

    def get_queryset(self):
        return Shift.objects.filter(employee=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        self.object = self.get_queryset()

        if not self.object:
            context_dict = ['No shifts available for this given query.']
        else:
            context_dict = [{
                u"employee": shift.employee.username,
                u"contract": shift.contract_or_none,
                u"shift_started": shift.shift_started,
                u"shift_finished": shift.shift_finished,
                u"pause_duration": shift.pause_duration,
                u"shift_duration": shift.shift_duration
            } for shift in self.object]

        return self.render_json_response(context_dict)


class ExportContractMonthAPI(ExportMonthClass):
    def get_queryset(self):
        contract_pk = self.kwargs['pk']
        return Shift.objects.filter(
            employee=self.request.user.pk, contract=contract_pk)


class ExportMonthAPI(ExportMonthClass):
    pass
