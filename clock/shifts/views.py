from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic.dates import MonthArchiveView, YearArchiveView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from pytz import timezone as p_timezone

from clock.pages.mixins import UserObjectOwnerMixin
from clock.shifts.forms import ClockInForm, ClockOutForm, ShiftForm
from clock.shifts.models import Shift
from clock.shifts.utils import (
    get_all_contracts,
    get_current_shift,
    get_default_contract,
    get_return_url,
    set_correct_session,
)


@require_POST
@login_required
def shift_action(request):
    # Get the current Shift object
    shift = get_current_shift(request.user)

    if not shift and '_start' not in request.POST:
        messages.add_message(
            request, messages.ERROR,
            _('You need an active shift to perform this action!'), 'danger'
        )
        return redirect('home')
    elif shift and '_start' in request.POST:
        messages.add_message(
            request, messages.ERROR, _('You already have an active shift!'),
            'danger'
        )
        return redirect('home')

    # Start a new shift
    if '_start' in request.POST:
        contract = None
        if 'contract' in request.POST:
            contract = request.POST['contract']
        form = ClockInForm(
            data={
                'started': timezone.now(),
                'contract': contract
            },
            user=request.user
        )

        if form.is_valid():
            form.clock_in()
            # Show a success message
            messages.add_message(
                request, messages.SUCCESS, _('Your shift has started!')
            )
        else:
            messages.add_message(request, messages.ERROR, form.errors)

    # Stop current shift
    elif '_stop' in request.POST:
        # Set the finished value to timezone.now() and save the updated shift
        form = ClockOutForm(data={'finished': timezone.now()}, instance=shift)

        if form.is_valid():
            form.clock_out()
            messages.add_message(
                request, messages.SUCCESS, _('Your shift has finished!')
            )
        else:
            messages.add_message(
                request, messages.WARNING, form.errors['__all__']
            )

    return redirect('home')


@method_decorator(login_required, name="dispatch")
class ShiftListView(ListView):
    model = Shift
    template_name = 'shift/list.html'

    def get_queryset(self):
        return Shift.objects.filter(
            employee=self.request.user.id, finished__isnull=False
        )


@method_decorator(login_required, name="dispatch")
class ShiftManualCreate(CreateView):
    model = Shift
    form_class = ShiftForm
    template_name = 'shift/edit.html'

    def get_success_url(self):
        return get_return_url(self.request, 'shift:list')

    def get_form_kwargs(self):
        """
        Add some specific kwargs that our Form needs to display everything
        correctly.
        """
        kwargs = super(ShiftManualCreate, self).get_form_kwargs()
        k = {
            'request': self.request,
            'view': 'shift_create',
            'contract': set_correct_session(self.request, 'contract'),
            'user': self.request.user
        }
        kwargs.update(k)
        return kwargs

    @property
    def start_datetime(self):
        try:
            d = datetime(
                int(self.request.session['last_kwargs']['year']),
                int(self.request.session['last_kwargs']['month']),
                1,
                hour=8
            ).strftime("%Y-%m-%dT%H:%M")
            if self.request.session['last_kwargs']['month'] == datetime.now(
            ).strftime("%m"):
                d = datetime.now().strftime("%Y-%m-%dT%H:%M")
        except KeyError:
            d = datetime.now().strftime("%Y-%m-%dT%H:%M")

        return d


@method_decorator(login_required, name="dispatch")
class ShiftManualEdit(UpdateView, UserObjectOwnerMixin):
    model = Shift
    form_class = ShiftForm
    template_name = 'shift/edit.html'

    def get_success_url(self):
        return get_return_url(self.request, 'shift:list')

    def get_form_kwargs(self):
        """
        Add some specific kwargs that our Form needs to display everything
        correctly.
        """
        kwargs = super(ShiftManualEdit, self).get_form_kwargs()
        k = {
            'request': self.request,
            'view': 'shift_update',
            'contract': set_correct_session(self.request, 'contract'),
            'user': self.request.user
        }
        kwargs.update(k)
        return kwargs

    def get_shift(self):
        # Use the current timezone when retrieving datetime objects
        tz = p_timezone(settings.TIME_ZONE)

        moment_format = "%Y-%m-%dT%H:%M"
        obj = self.get_object()
        dates = {
            'started': obj.started.astimezone(tz).strftime(moment_format),
            'finished': obj.finished.astimezone(tz).strftime(moment_format)
        }
        return dates


@method_decorator(login_required, name="dispatch")
class ShiftManualDelete(DeleteView, UserObjectOwnerMixin):
    model = Shift
    template_name = 'shift/delete.html'

    def get_success_url(self):
        return get_return_url(self.request, 'shift:list')


@method_decorator(login_required, name="dispatch")
class ShiftMonthView(MonthArchiveView):
    date_field = "started"
    allow_empty = True
    allow_future = True
    template_name = 'shift/month_archive_view.html'

    class Meta:
        ordering = ["-started"]

    def dispatch(self, request, *args, **kwargs):
        """
        Set the current year and month, if those values were not supplied in
        the URL.
        """
        self.year = kwargs.get('year', timezone.now().strftime("%Y"))
        self.month = kwargs.get('month', timezone.now().strftime("%m"))

        return super(ShiftMonthView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Shift.objects.filter(
            employee=self.request.user, finished__isnull=False
        )

    @property
    def get_all_contracts(self):
        return get_all_contracts(self.request.user)

    @property
    def get_default_contract(self):
        return get_default_contract(self.request.user)


@method_decorator(login_required, name="dispatch")
class ShiftMonthContractView(ShiftMonthView):
    """
    Show all shifts assigned to a contract of a specific date.
    The contract pk may be either:
        '0': Show shifts not assigned to any contract
        '00': Show all shifts without any contract filtering (default)
        '<contract>': Show shifts assigned to contract with the id <contract>
    """
    contract = '00'

    def dispatch(self, request, *args, **kwargs):
        """Grab contract numeric-string from URL if the value was passed. Otherwise
        use a default of '00'.
        """
        self.contract = kwargs.get('contract', self.contract)

        return super(ShiftMonthContractView,
                     self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Shift.objects.filter(
            employee=self.request.user.pk, finished__isnull=False
        )
        if self.contract == "0":
            queryset = queryset.filter(contract__isnull=True)
        elif self.contract == '00':
            pass
        else:
            queryset = queryset.filter(contract=self.contract)
        return queryset


@method_decorator(login_required, name="dispatch")
class ShiftYearView(YearArchiveView):
    date_field = "started"
    allow_future = False
    allow_empty = True
    template_name = 'shift/year_archive_view.html'

    def get_queryset(self):
        return Shift.objects.filter(employee=self.request.user
                                    ).order_by('started')
