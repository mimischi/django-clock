# -*- coding: utf-8 -*-
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.dates import MonthArchiveView

from braces.views import JSONResponseMixin

from clock.shifts.models import Shift
from clock.exports.mixins import PdfResponseMixin
from clock.exports.serializers import ShiftJSONEncoder


@method_decorator(login_required, name="dispatch")
class ExportMonth(PdfResponseMixin, MonthArchiveView):
    Model = Shift
    date_field = "shift_started"

    def get_context_data(self, **kwargs):
        context = super(ExportMonth, self).get_context_data(**kwargs)

        total_shift_duration = timedelta(seconds=0)
        for shift in context['shift_list']:
            total_shift_duration += shift.shift_duration
            context['total_shift_duration'] = total_shift_duration
        return context

    def get_queryset(self):
        contract_pk = self.kwargs['pk']
        return Shift.objects.filter(employee=self.request.user.pk, contract=contract_pk, shift_finished__isnull=False)


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

        # gen = StundenzettelGenerator(example_template, example_target, example_data, context_dict)
        #
        # gen.make()

        return self.render_json_response(context_dict)


class ExportContractMonthAPI(ExportMonthClass):
    def get_queryset(self):
        contract_pk = self.kwargs['pk']
        return Shift.objects.filter(employee=self.request.user.pk, contract=contract_pk)


class ExportMonthAPI(ExportMonthClass):
    pass
