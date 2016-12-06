from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, TemplateView

from clock.contact.forms import ContactForm


class ContactView(FormView):
    template_name = 'contact/form.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:success')

    def form_valid(self, form):
        form.send_mail(form)
        return super(ContactView, self).form_valid(form)


class ContactSuccessView(TemplateView):
    template_name = 'contact/success.html'
