# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.views.generic import TemplateView

from clock.profiles.views import delete_user

from . import views

urlpatterns = [
    url(
        r'^profiles/$',
        view=views.AccountUpdateView.as_view(),
        name='account_view'),
    url(r'^delete/', delete_user, name="delete"),
    url(
        r'^goodbye/',
        TemplateView.as_view(template_name='profiles/goodbye.html'),
        name="goodbye"),
]
