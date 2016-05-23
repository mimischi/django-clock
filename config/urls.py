# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView
from django.views import defaults as default_views

urlpatterns = [
                  url(r'^', include("clock.pages.urls"), name='pages'),
                  url(r'^about/$', views.flatpage, {'url': '/about/'}, name='about'),
                  url(
                      r'^favicon.ico$',
                      RedirectView.as_view(
                          url=staticfiles_storage.url('common/images/favicon.ico'),
                          permanent=False),
                      name="favicon"
                  ),

                  # Django Admin
                  url(r'^admin/', include(admin.site.urls)),

                  # User management
                  url(r'^accounts/', include("clock.account.urls", namespace="account")),
                  url(r'^accounts/', include('allauth.urls')),

                  # Your stuff: custom urls includes go here
                  # Include urls fot the work module
                  url(r'^i18n/', include('django.conf.urls.i18n')),
                  url(r'^shift/', include("clock.shifts.urls", namespace="shift")),
                  url(r'^contract/', include("clock.contracts.urls", namespace="contract")),
                  url(r'^export/', include("clock.exports.urls", namespace="export")),
                  # url(r'^', include("clock.work.urls", namespace="work")),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception("Bad Request!")}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception("Permission Denied")}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception("Page not Found")}),
        url(r'^500/$', default_views.server_error),
    ]

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^rosetta/', include('rosetta.urls')),
    ]
