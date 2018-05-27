# -*- coding: utf-8 -*-
from django.urls import path

from clock.contracts.views import (
    ContractAddView,
    ContractDeleteView,
    ContractListView,
    ContractUpdateView,
)

app_name = "contract"
urlpatterns = [
    # Contract URLs
    # ListView for all contracts of one employee
    path("", ContractListView.as_view(), name="list"),
    # CreateView to add a new contract
    path("new/", ContractAddView.as_view(), name="new"),
    # UpdateView to update an existing contract
    path("<int:pk>/edit/", ContractUpdateView.as_view(), name="edit"),
    # DeleteView to delete an existing contract
    path("<int:pk>/delete/", ContractDeleteView.as_view(), name="delete"),
]
