# -*- coding: utf-8 -*-

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:    # Django < 1.10
    # Works perfectly for everyone using MIDDLEWARE_CLASSES
    MiddlewareMixin = object


# Adapted from https://djangosnippets.org/snippets/248/
class LastVisitedMiddleware(MiddlewareMixin):
    """This middleware sets the last visited url as session field"""

    def process_view(self, request, view_func, view_args, view_kwargs):
        request_path = request.get_full_path()
        request_kwargs = view_kwargs
        request_view_name = request.resolver_match.view_name
        try:
            # Added a check whether we're visiting a UpdateView right now. This
            # will now redirect to the old ListView, as otherwise the kwargs
            # would be overwritten and we'd be redirected to the default one.
            if request.session['currently_visiting'] != request_path and (
                    'delete' not in request_view_name):
                request.session['last_visited'] = request.session[
                    'currently_visiting']
                request.session['last_kwargs'] = request.session[
                    'current_kwargs']
                request.session['last_view_name'] = request.session[
                    'current_view_name']
            request.session['last_real_visited'] = request.session[
                'currently_visiting']
        except KeyError:
            pass

        # We're sometimes calling the view with init-kwargs, instead of passing
        # them as GET parameters
        if not request_kwargs:
            try:
                request_kwargs = view_func.__dict__['view_initkwargs']
            except KeyError:
                pass

        request.session['currently_visiting'] = request_path
        request.session['current_kwargs'] = request_kwargs
        request.session['current_view_name'] = request_view_name

        return None
