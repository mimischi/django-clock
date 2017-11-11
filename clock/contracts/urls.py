# -*- coding: utf-8 -*-
from django.conf.urls import url

from clock.contracts.views import (
    ContractAddView,
    ContractDeleteView,
    ContractListView,
    ContractUpdateView,
)

urlpatterns = [
    # Contract URLs
    # ListView for all contracts of one employee
    url(r'^$', ContractListView.as_view(), name="list"),
    # CreateView to add a new contract
    url(r'^new/$', ContractAddView.as_view(), name='new'),
    # UpdateView to update an existing contract
    url(r'^(?P<pk>\d+)/edit/$', ContractUpdateView.as_view(), name='edit'),
    # DeleteView to delete an existing contract
    url(r'^(?P<pk>\d+)/delete/$', ContractDeleteView.as_view(), name='delete'),
]
