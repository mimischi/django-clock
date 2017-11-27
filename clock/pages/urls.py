# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from clock.pages import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
]
