# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView, TemplateView
from django.views import defaults

from clock.work import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(
        r'^favicon.ico$',
        RedirectView.as_view(
            url=staticfiles_storage.url('img/favicon.ico'),
            permanent=False),
        name="favicon"
    ),
    url(r'^about/$', TemplateView.as_view(
        template_name='pages/about.html'),
        name="about"),

    # Django Admin
    url(r'^admin/', include(admin.site.urls)),

    # User management
    url(r'^accounts/', include("clock.account.urls", namespace="account")),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    # Include urls fot the work module
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^', include("clock.work.urls", namespace="work")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', defaults.bad_request),
        url(r'^403/$', defaults.permission_denied),
        url(r'^404/$', defaults.page_not_found),
        url(r'^500/$', defaults.server_error),
    ]

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^rosetta/', include('rosetta.urls')),
    ]
