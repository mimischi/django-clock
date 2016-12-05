from braces.views import LoginRequiredMixin
from django import http
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import translate_url, reverse_lazy
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.utils.translation import LANGUAGE_SESSION_KEY, check_for_language
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from clock.users.models import User
from clock.profiles.forms import UpdateUserForm, DeleteUserForm
from clock.profiles.models import UserProfile

LANGUAGE_QUERY_PARAMETER = 'language'


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/profile.html'


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    """View to update some profile information."""
    model = User
    form_class = UpdateUserForm
    template_name = 'profiles/profile.html'
    success_url = reverse_lazy('profiles:account_view')

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)


@login_required()
def update_language(request):
    """
    This is a very lazy solution overwriting django.views.i18n.set_lang. We're basically just adding another option
    to save the selected language into the database, besides the session. This way we can retrieve the language
    preference across different devices and after a longer period of time, when the user was not logged in.

    It's possible, that there is a nifty trick on how to make this whole thing shorter and not having to copy the whole
    function. But this seems to work so far.
    """
    next = request.POST.get('next', request.GET.get('next'))
    if not is_safe_url(url=next, host=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, host=request.get_host()):
            next = '/'
    response = http.HttpResponseRedirect(next)
    if request.method == 'POST':
        lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
        if lang_code and check_for_language(lang_code):
            next_trans = translate_url(next, lang_code)
            if next_trans != next:
                response = http.HttpResponseRedirect(next_trans)
            if hasattr(request, 'session'):
                obj, created = UserProfile.objects.get_or_create(
                    user=request.user,
                    defaults={'language': lang_code},
                )
                if not created:
                    obj.language = lang_code
                    obj.save()
                request.session[LANGUAGE_SESSION_KEY] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code,
                                    max_age=settings.LANGUAGE_COOKIE_AGE,
                                    path=settings.LANGUAGE_COOKIE_PATH,
                                    domain=settings.LANGUAGE_COOKIE_DOMAIN)
    return response


@login_required()
def delete_user(request):
    template_name = 'profiles/delete.html'
    context = {'text': _('<p>Are you sure you want to delete this profile? Please type in your username '
                         '<strong>%s</strong> to confirm.</p>') % request.user}

    if request.method == 'POST':
        form = DeleteUserForm(request.POST, user=request.user)

        if form.is_valid():
            User = get_user_model()

            User.objects.get(username=request.user).delete()
            return redirect('goodbye')

    else:
        form = DeleteUserForm()

    context['form'] = form
    return render(request, template_name=template_name, context=context)
