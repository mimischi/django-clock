# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from clock.exports.views import ExportMonth, ExportMonthAPI, ExportContractMonthAPI, ExportNuke

urlpatterns = [
    # Export URLs
    url(
        r'^(?P<year>[0-9]{4})/(?P<month>[0-9]+)/contract/(?P<pk>\d+)/$',
        ExportMonth.as_view(month_format='%m'),
        name="contract"),
    url(
        r'^api/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/$',
        ExportMonthAPI.as_view(month_format='%m'),
        name="api_all"),
    # ListView for all shifts of a contract in a month
    url(
        r'^api/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/contract/(?P<pk>\d+)/$',
        ExportContractMonthAPI.as_view(month_format='%m'),
        name='api_contract'),
    url(
        r'^(?P<year>[0-9]{4})/(?P<month>[0-9]+)/contract/(?P<pk>\d+)/hours/(?P<hours>\d+)/nuke/$',
        ExportNuke.as_view(month_format='%m'),
        name="contract_nuke"),
]
