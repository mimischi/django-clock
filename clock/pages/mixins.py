from django.http import Http404
from django.views.generic.detail import SingleObjectMixin


class UserObjectOwnerMixin(SingleObjectMixin):
    """
    Overrides SingleObjectMixin and checks if the user actually created the requested object.
    """

    def get_object(self, queryset=None):
        obj = super(UserObjectOwnerMixin, self).get_object(queryset)
        if obj.employee != self.request.user:
            raise Http404
        return obj
