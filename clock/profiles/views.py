from braces.views import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from clock.profiles.forms import DeleteUserForm


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/profile.html'


@login_required()
def delete_user(request):
    template_name = 'profiles/delete.html'
    context = {'text': _('<p>Are you sure you want to delete this profile? Please type in your username '
                         '<strong>%s</strong> to confirm.</p>' % request.user)}

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
