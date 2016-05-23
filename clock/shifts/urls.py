# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.conf.urls import url

from clock.shifts.utils import get_default_contract
from clock.shifts.views import ShiftListView, ShiftManualCreate, \
    ShiftManualEdit, ShiftManualDelete, ShiftYearView
from clock.shifts.views import ShiftMonthView, ShiftMonthContractView, ShiftWeekView, ShiftYearView, ShiftDayView, \
    shift_action

# Data to display the current year-month inside the shift_list
currentDate = datetime.now()
currentYear = currentDate.strftime("%Y")
currentMonth = currentDate.strftime("%m")

urlpatterns = [
    # Shift URLs
    # ListView for all finished shifts of one employee
    # url(r'^shift/$', ShiftListView.as_view(),
    #     name="shift_list"
    #     ),

    # Display the ShiftMonthView as default with the current year-month
    url(r'^$', ShiftMonthContractView.as_view(month_format='%m', year=currentYear, month=currentMonth),
        name="list"
        ),
    # View to handle all the quick-actions from the dashboard
    url(r'^quick_action/$', shift_action,
        name='quick_action'),
    # CreateView to add a new shift
    url(r'^new/$',
        ShiftManualCreate.as_view(),
        name='new'
        ),
    # UpdateView to update an existing shift
    url(r'^(?P<pk>\d+)/edit/$',
        ShiftManualEdit.as_view(),
        name='edit'
        ),
    # DeleteView to delete an existing shift
    url(r'^(?P<pk>\d+)/delete/$',
        ShiftManualDelete.as_view(),
        name='delete'
        ),

    # Shift Archive URLs
    url(r'^archive/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<day>[0-9]+)/$',
        ShiftDayView.as_view(),
        name="archive_day"),
    url(r'^archive/(?P<year>[0-9]{4})/week/(?P<week>[0-9]+)/$',
        ShiftWeekView.as_view(),
        name="archive_week"),
    url(r'^archive/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/$',
        ShiftMonthContractView.as_view(month_format='%m'),
        name="archive_month_numeric"),
    url(r'^archive/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/contract/(?P<contract>\d+)/$',
        ShiftMonthContractView.as_view(month_format='%m'),
        name="archive_month_contract_numeric"),
    url(r'^archive/(?P<year>[0-9]{4})/$',
        ShiftYearView.as_view(),
        name="article_year_archive"),
    ]
