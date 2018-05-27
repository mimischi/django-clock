# -*- coding: utf-8 -*-
from django.urls import path

from . import views

urlpatterns = [
    # URL pattern for the UserListView
    path("", view=views.UserListView.as_view(), name="account_view"),
    # URL pattern for the UserRedirectView
    path("~redirect/", view=views.UserRedirectView.as_view(), name="redirect"),
    # URL pattern for the UserDetailView
    path("<str:username>/", view=views.UserDetailView.as_view(), name="detail"),
    # URL pattern for the UserUpdateView
    path("~update/", view=views.UserUpdateView.as_view(), name="update"),
]
