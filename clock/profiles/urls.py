# -*- coding: utf-8 -*-
from django.urls import path
from django.views.generic import TemplateView

from clock.profiles.views import delete_user

from . import views

app_name = "profiles"
urlpatterns = [
    path("profiles/", view=views.AccountUpdateView.as_view(), name="account_view"),
    path("delete/", delete_user, name="delete"),
    path(
        "goodbye/",
        TemplateView.as_view(template_name="profiles/goodbye.html"),
        name="goodbye",
    ),
]
