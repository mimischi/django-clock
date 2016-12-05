# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.views.generic.dates import MonthArchiveView

from braces.views import JSONResponseMixin

from clock.contracts.models import Contract
from clock.exports.mixins import PdfResponseMixin
from clock.exports.serializers import ShiftJSONEncoder
from clock.shifts.models import Shift

from clock.exports.stundenzettel_generator.standupstrategy import StandupStrategy


@method_decorator(login_required, name="dispatch")
class ExportMonth(PdfResponseMixin, MonthArchiveView):
    model = Shift
    date_field = "shift_started"
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super(ExportMonth, self).get_context_data(**kwargs)

        # TODO: Can result in text overflowing the drawn box!
        context['fullname'] = '{} {}'.format(self.request.user.first_name, self.request.user.last_name)

        if not context['shift_list']:
            context['department'] = Contract.objects.get(pk=int(self.kwargs['pk'])).department
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
        return Shift.objects.filter(employee=self.request.user.pk, contract=contract_pk, shift_finished__isnull=False)


@method_decorator(login_required, name="dispatch")
class ExportNuke(PdfResponseMixin, MonthArchiveView):
    model = Shift
    date_field = "shift_started"

    def get_context_data(self, **kwargs):
        context = super(ExportNuke, self).get_context_data(**kwargs)

        if int(context['view'].kwargs['hours']) > 80:
            raise HttpResponseBadRequest(_('We can\'t export more than 80 hours per month!'))

        context['department'] = get_object_or_404(Contract, employee=self.request.user,
                                                  pk=int(self.kwargs['pk'])).department

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
            total_shift_duration += timedelta(seconds=shifts['working_hours'] * 3600)

            shift_total_pause_duration = timedelta(seconds=0)
            if shifts['break_start'] is not None:
                start = (shifts['break_start'] - datetime(1970, 1, 1)).total_seconds()
                end = (shifts['break_end'] - datetime(1970, 1, 1)).total_seconds()
                shift_pause = end - start

                shift_total_pause_duration = timedelta(seconds=shift_pause)
            shift_list.append(Shift(
                shift_started=shifts['daystart'],
                shift_finished=shifts['work_end'],
                shift_duration=timedelta(seconds=shifts['working_hours'] * 3600),
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
