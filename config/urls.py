# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse
from django.views import defaults as default_views
from django.views.generic import RedirectView

import clock.profiles.views

urlpatterns = [
                  url(r'^', include("clock.pages.urls"), name='pages'),
                  url(r'^about/$', views.flatpage, {'url': '/about/'}, name='about'),
                  url(r'^impressum/$', views.flatpage, {'url': '/impressum/'}, name='imprint'),
                  url(r'^privacy/$', views.flatpage, {'url': '/privacy/'}, name='privacy'),
                  url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")),
                  url(
                      r'^favicon.ico$',
                      RedirectView.as_view(
                          url=staticfiles_storage.url('common/favicons/favicon.ico'),
                          permanent=False),
                      name="favicon"
                  ),
                  url(r'^apple-touch-icon-57x57.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/apple-touch-icon-57x57.png'),
                                           permanent=False)),
                  url(r'^apple-touch-icon-60x60.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/apple-touch-icon-60x60.png'),
                                           permanent=False)),
                  url(r'^apple-touch-icon-72x72.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/apple-touch-icon-72x72.png'),
                                           permanent=False)),
                  url(r'^apple-touch-icon-76x76.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/apple-touch-icon-76x76.png'),
                                           permanent=False)),
                  url(r'^apple-touch-icon-114x114.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/apple-touch-icon-114x114.png'),
                                           permanent=False)),
                  url(r'^apple-touch-icon-120x120.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/apple-touch-icon-120x120.png'),
                                           permanent=False)),
                  url(r'^apple-touch-icon-144x144.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/apple-touch-icon-144x144.png'),
                                           permanent=False)),
                  url(r'^apple-touch-icon-152x152.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/apple-touch-icon-152x152.png'),
                                           permanent=False)),
                  url(r'^apple-touch-icon-180x180.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/apple-touch-icon-180x180.png'),
                                           permanent=False)),
                  url(r'^favicon-32x32.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/favicon-32x32.png'),
                                           permanent=False)),
                  url(r'^android-chrome-192x192.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/android-chrome-192x192.png'),
                                           permanent=False)),
                  url(r'^favicon-96x96.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/favicon-96x96.png'),
                                           permanent=False)),
                  url(r'^favicon-16x16.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/favicon-16x16.png'),
                                           permanent=False)),
                  url(r'^manifest.json',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/manifest.json'),
                                           permanent=False)),
                  url(r'^safari-pinned-tab.svg',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/safari-pinned-tab.svg'),
                                           permanent=False)),
                  url(r'^mstile-144x144.png',
                      RedirectView.as_view(url=staticfiles_storage.url('common/favicons/mstile-144x144.png'),
                                           permanent=False)),

                  # Django Admin
                  url(r'^admin/', include(admin.site.urls)),

                  # User management
                  url(r'^accounts/', include("clock.profiles.urls", namespace="profiles")),
                  url(r'^accounts/', include('allauth.urls')),

                  # Your stuff: custom urls includes go here
                  # Include urls fot the work module
                  url(r'^i18n/updatelanguage', clock.profiles.views.update_language, name='update_language'),
                  url(r'^i18n/', include('django.conf.urls.i18n')),
                  url(r'^shift/', include("clock.shifts.urls", namespace="shift")),
                  url(r'^contract/', include("clock.contracts.urls", namespace="contract")),
                  url(r'^export/', include("clock.exports.urls", namespace="export")),
                  url(r'^contact/', include("clock.contact.urls", namespace="contact")),
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
