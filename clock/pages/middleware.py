# -*- coding: utf-8 -*-


# Adapted from https://djangosnippets.org/snippets/248/
class LastVisitedMiddleware(object):
    """This middleware sets the last visited url as session field"""

    def process_view(self, request, view_func, view_args, view_kwargs):
        request_path = request.get_full_path()
        request_kwargs = view_kwargs
        request_view_name = request.resolver_match.view_name

        try:
            if request.session['currently_visiting'] != request_path:
                request.session['last_visited'] = request.session['currently_visiting']
                request.session['last_kwargs'] = request.session['current_kwargs']
                request.session['last_view_name'] = request.session['current_view_name']
            request.session['last_real_visited'] = request.session['currently_visiting']
        except KeyError:
            pass

        # We're sometimes calling the view with init-kwargs, instead of passing them as GET parameters
        if not request_kwargs:
            try:
                request_kwargs = view_func.func_dict['view_initkwargs']
            except KeyError:
                pass

        request.session['currently_visiting'] = request_path
        request.session['current_kwargs'] = request_kwargs
        request.session['current_view_name'] = request_view_name
