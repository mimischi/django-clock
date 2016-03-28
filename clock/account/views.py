from braces.views import LoginRequiredMixin
from django.views.generic import UpdateView, TemplateView


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'account/profile.html'
