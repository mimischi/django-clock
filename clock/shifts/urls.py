# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.utils import timezone

from clock.shifts.views import ShiftManualCreate, \
    ShiftManualEdit, ShiftManualDelete
from clock.shifts.views import ShiftMonthContractView, ShiftWeekView, ShiftYearView, ShiftDayView, \
    shift_action

urlpatterns = [
    # Shift URLs
    # Display the ShiftMonthView as default with the current year-month
    url(r'^$', ShiftMonthContractView.as_view(month_format='%m',
                                              year=timezone.now().strftime("%Y"),
                                              month=timezone.now().strftime("%m")),
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
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<day>[0-9]+)/$',
        ShiftDayView.as_view(),
        name="archive_day"),
    url(r'^(?P<year>[0-9]{4})/week/(?P<week>[0-9]+)/$',
        ShiftWeekView.as_view(),
        name="archive_week"),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]+)/$',
        ShiftMonthContractView.as_view(month_format='%m'),
        name="archive_month_numeric"),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]+)/contract/(?P<contract>\d+)/$',
        ShiftMonthContractView.as_view(month_format='%m'),
        name="archive_month_contract_numeric"),
    url(r'^(?P<year>[0-9]{4})/$',
        ShiftYearView.as_view(),
        name="article_year_archive"),
    ]
