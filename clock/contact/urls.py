# -*- coding: utf-8 -*-


from django.conf.urls import url

from clock.contact.views import ContactView, ContactSuccessView

urlpatterns = [
    url(r'^$', ContactView.as_view(), name="form"),
    url(r'^success/$', ContactSuccessView.as_view(), name="success"),
]
