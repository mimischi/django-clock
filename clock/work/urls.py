# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from clock.work.views import ShiftListView, ShiftManualCreate, \
    ShiftManualEdit, ShiftManualDelete
from clock.work.views import ContractListView, ContractAddView, \
    ContractUpdateView, ContractDeleteView

from clock.work.views import ShiftMonthView, ShiftWeekView

urlpatterns = [
    url(r'^(?P<year>[0-9]{4})/week/(?P<week>[0-9]+)/$',
        ShiftWeekView.as_view(),
        name="archive_week"),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]+)/$',
        ShiftMonthView.as_view(month_format='%m'),
        name="archive_month_numeric"),


    # Contract URLs
    # ListView for all contracts of one employee
    url(r'^contract/$', ContractListView.as_view(),
        name="contract_list"
        ),
    # CreateView to add a new contract
    url(r'^contract/add/$',
        ContractAddView.as_view(),
        name='contract_add'),
    # UpdateView to update an existing contract
    url(r'^contract/(?P<pk>\d+)/update/$',
        ContractUpdateView.as_view(),
        name='contract_edit'
        ),
    # DeleteView to delete an existing contract
    url(r'^contract/(?P<pk>\d+)/delete/$',
        ContractDeleteView.as_view(),
        name='contract_delete'
        ),

    # Shift URLs
    # ListView for all finished shifts of one employee
    url(r'^shift/$', ShiftListView.as_view(),
        name="shift_list"
        ),
    # View to handle all the quick-actions from the dashboard
    url(r'^shift/quick_action/$', 'clock.work.views.shift_action',
        name='quick_action'),
    # CreateView to add a new shift
    url(r'^shift/add/$',
        ShiftManualCreate.as_view(),
        name='shift_add'
        ),
    # UpdateView to update an existing shift
    url(r'^shift/(?P<pk>\d+)/update/$',
        ShiftManualEdit.as_view(),
        name='shift_edit'
        ),
    # DeleteView to delete an existing shift
    url(r'^shift/(?P<pk>\d+)/delete/$',
        ShiftManualDelete.as_view(),
        name='shift_delete'
        ),
    ]
