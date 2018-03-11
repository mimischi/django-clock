# -*- coding: utf-8 -*-
from django.urls import path

from clock.contact.views import ContactSuccessView, ContactView

app_name = 'contact'
urlpatterns = [
    path('', ContactView.as_view(), name="form"),
    path('success/', ContactSuccessView.as_view(), name="success"),
]
