from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from clock.contracts.forms import ContractForm
from clock.contracts.models import Contract
from clock.pages.mixins import UserObjectOwnerMixin


@method_decorator(login_required, name="dispatch")
class ContractListView(ListView):
    model = Contract
    template_name = 'contract/list.html'

    def get_queryset(self):
        return Contract.objects.filter(employee=self.request.user.id)


@method_decorator(login_required, name="dispatch")
class ContractAddView(CreateView):
    model = Contract
    template_name = 'contract/edit.html'
    form_class = ContractForm
    success_url = reverse_lazy('contract:list')

    def get_form_kwargs(self):
        """
        Add some specific kwargs that our Form needs to display everything
        correctly.
        """
        kwargs = super().get_form_kwargs()
        k = {'view': 'create', 'user': self.request.user}
        kwargs.update(k)
        return kwargs

    def form_valid(self, form):
        contract = form.save(commit=False)
        contract.employee = self.request.user

        contract.save()
        return super(ContractAddView, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
class ContractUpdateView(UpdateView, UserObjectOwnerMixin):
    model = Contract
    template_name = 'contract/edit.html'
    form_class = ContractForm
    success_url = reverse_lazy('contract:list')

    def get_form_kwargs(self):
        """
        Add some specific kwargs that our Form needs to display everything
        correctly.
        """
        kwargs = super().get_form_kwargs()
        k = {'view': 'update', 'user': self.request.user}
        kwargs.update(k)
        return kwargs


@method_decorator(login_required, name="dispatch")
class ContractDeleteView(DeleteView, UserObjectOwnerMixin):
    model = Contract
    success_url = reverse_lazy('contract:list')
    template_name = 'contract/delete.html'

    def get_queryset(self):
        """
        Return our own contracts and not those of other employees.
        """
        return self.request.user.contract_set.all()
