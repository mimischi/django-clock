# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.dates import MonthArchiveView

from braces.views import JSONResponseMixin

from clock.shifts.models import Shift
from clock.exports.mixins import PdfResponseMixin
from clock.exports.serializers import ShiftJSONEncoder

from clock.exports.stundenzettel_generator.standupstrategy import StandupStrategy


@method_decorator(login_required, name="dispatch")
class ExportMonth(PdfResponseMixin, MonthArchiveView):
    model = Shift
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
class ExportNuke(PdfResponseMixin, MonthArchiveView):
    model = Shift
    date_field = "shift_started"

    def get_context_data(self, **kwargs):
        context = super(ExportNuke, self).get_context_data(**kwargs)

        nuke_data = {
            'INSTITUT': '',
            'NAME': '',
            'MONAT': context['view'].kwargs['month'] + " / " + context['view'].kwargs['year'],
            'PERSNR': '',  # just left blank

            # these parameters drive the simulation
            'month': int(context['view'].kwargs['month']), 'year': int(context['view'].kwargs['year']),
            'monthly_hours': int(context['view'].kwargs['hours']), 'hours': int(context['view'].kwargs['hours'])
        }

        nuke = StandupStrategy(nuke_data)
        test = nuke.createSchedule()

        total_shift_duration = timedelta(seconds=0)
        shift_list = []
        for shifts in test:
            total_shift_duration += timedelta(seconds=shifts['working_hours']*3600)

            shift_total_pause_duration = timedelta(seconds=0)
            if shifts['break_start'] is not None:
                start = (shifts['break_start'] - datetime(1970, 1, 1)).total_seconds()
                end = (shifts['break_end'] - datetime(1970, 1, 1)).total_seconds()
                shift_pause = end - start

                shift_total_pause_duration = timedelta(seconds=shift_pause)
            shift_list.append(Shift(
                shift_started=shifts['daystart'],
                shift_finished=shifts['work_end'],
                shift_duration=timedelta(seconds=shifts['working_hours']*3600),
                pause_duration=shift_total_pause_duration,
                )
            )

        context['total_shift_duration'] = total_shift_duration
        context['shift_list'] = shift_list

        return context


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
        return Shift.objects.filter(employee=self.request.user.pk, contract=contract_pk)


class ExportMonthAPI(ExportMonthClass):
    pass
