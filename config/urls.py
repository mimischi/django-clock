# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from config.favicon_urls import favicon_urlpatters
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.http import HttpResponse
from django.views import defaults as default_views

import clock.profiles.views

urlpatterns = [
                  url(r'^', include("clock.pages.urls"), name='pages'),
                  url(r'^about/$', views.flatpage, {'url': '/about/'}, name='about'),
                  url(r'^impressum/$', views.flatpage, {'url': '/impressum/'}, name='imprint'),
                  url(r'^privacy/$', views.flatpage, {'url': '/privacy/'}, name='privacy'),
                  url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")),

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

# Add all needed favicon redirects to comply with todays OS/browser standards
# urlpatterns += favicon_urlpatters

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$',
            default_views.bad_request,
            kwargs={'exception': Exception("Bad Request!")}),
        url(r'^403/$',
            default_views.permission_denied,
            kwargs={'exception': Exception("Permission Denied")}),
        url(r'^404/$',
            default_views.page_not_found,
            kwargs={'exception': Exception("Page not Found")}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^rosetta/', include('rosetta.urls')),
    ]
