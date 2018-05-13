# -*- coding: utf-8 -*-
from django.urls import path

from clock.shifts.views import (
    ShiftManualCreate,
    ShiftManualDelete,
    ShiftManualEdit,
    ShiftMonthContractView,
    ShiftYearView,
    shift_action,
)

app_name = 'shift'
urlpatterns = [
    # Shift URLs
    # Display the ShiftMonthView as default with the current year-month
    path('', ShiftMonthContractView.as_view(month_format='%m', ), name="list"),
    # View to handle all the quick-actions from the dashboard
    path('quick_action/', shift_action, name='quick_action'),
    # CreateView to add a new shift
    path('new/', ShiftManualCreate.as_view(), name='new'),
    # UpdateView to update an existing shift
    path('<int:pk>/edit/', ShiftManualEdit.as_view(), name='edit'),
    # DeleteView to delete an existing shift
    path('<int:pk>/delete/', ShiftManualDelete.as_view(), name='delete'),

    # Shift Archive URLs
    path(
        '<int:year>/<int:month>/',
        ShiftMonthContractView.as_view(month_format='%m'),
        name="archive_month_numeric"
    ),
    path(
        '<int:year>/<int:month>/contract/<str:contract>/',
        ShiftMonthContractView.as_view(month_format='%m'),
        name="archive_month_contract_numeric"
    ),
    path('<int:year>/', ShiftYearView.as_view(), name="article_year_archive"),
]
