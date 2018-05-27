# -*- coding: utf-8 -*-
from django.urls import path

from clock.pages import views

urlpatterns = [path("", views.home, name="home")]
