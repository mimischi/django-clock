# -*- coding: utf-8 -*-
from django.urls import path

from clock.exports.views import ExportContractMonthAPI, ExportMonth, ExportMonthAPI

app_name = "export"
urlpatterns = [
    # Export URLs
    path(
        "<int:year>/<int:month>/contract/<int:pk>/",
        ExportMonth.as_view(month_format="%m"),
        name="contract",
    ),
    path(
        "api/<int:year>/<int:month>/",
        ExportMonthAPI.as_view(month_format="%m"),
        name="api_all",
    ),
    # ListView for all shifts of a contract in a month
    path(
        "api/<int:year>/<int:month>/contract/<int:pk>/",
        ExportContractMonthAPI.as_view(month_format="%m"),
        name="api_contract",
    ),
]
