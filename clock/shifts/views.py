from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic.dates import DayArchiveView, MonthArchiveView, WeekArchiveView, YearArchiveView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView


from clock.pages.mixins import UserObjectOwnerMixin
from clock.shifts.forms import ShiftForm, QuickActionForm
from clock.shifts.models import Shift
from clock.shifts.utils import get_current_shift


@require_POST
@login_required
def shift_action(request):
    # Get the current shift (s) and the corresponding pauses (shift_pauses)
    shift = get_current_shift(request.user)

    if not shift and not '_start' in request.POST:
        messages.add_message(
            request,
            messages.ERROR,
            _('You need an active shift to perform this action!'),
            'danger'
        )
        return redirect('home')
    elif shift and '_start' in request.POST:
        messages.add_message(
            request,
            messages.ERROR,
            _('You already have an active shift!'),
            'danger'
        )
        return redirect('home')

    # Start a new shift
    if '_start' in request.POST:
        # Generate a new QuickActionForm, so we can retrieve the
        # supplied institute/contract the user has selected.
        # No other data will be looked at, as no validation of the
        # starting data is needed.
        form = QuickActionForm(request.POST, user=request.user)

        if form.is_valid():
            # Create a new shift, if the data is valid
            # (shouldn't this always be the case..?)
            Shift.objects.create(
                employee=request.user,
                contract=form.cleaned_data['contract'],
                shift_started=timezone.now()
            )
        else:
            Shift.objects.create(
                employee=request.user,
                shift_started=timezone.now()
            )

        # Show a success message
        messages.add_message(
            request,
            messages.SUCCESS,
            _('Your shift has started!')
        )

    # Stop current shift
    elif '_stop' in request.POST:
        # Unpause the shift, set the shift_finished value
        # to timezone.now() and save the updated shift
        shift.unpause()
        shift.shift_finished = timezone.now()
        shift.save()

        # Add a success message
        messages.add_message(
            request,
            messages.SUCCESS,
            _('Your shift has finished!')
        )

    # Toggle pause on current shift
    elif '_pause' in request.POST:
        # Toggle the pause value and save it
        shift.toggle_pause()
        shift.save()

        # Show a success message - either the pause was started or finished
        action = _('paused') if shift.is_paused else _('continued')
        message = 'Your shift was %s.' % action
        messages.add_message(request, messages.SUCCESS, message)

    return redirect('home')


@method_decorator(login_required, name="dispatch")
class ShiftListView(ListView):
    model = Shift
    template_name = 'shift/list.html'

    def get_queryset(self):
        return Shift.objects.filter(employee=self.request.user.id, shift_finished__isnull=False)


@method_decorator(login_required, name="dispatch")
class ShiftManualCreate(CreateView):
    model = Shift
    form_class = ShiftForm
    success_url = reverse_lazy('shift:list')
    template_name = 'shift/edit.html'

    def get_initial(self):
        """
        Sets initial data for the ModelForm, so we can use the user
        object and know which view created this form (CreateView in
        this case)
        """
        return {
            'user': self.request.user,
            'view': 'shift_create',
        }

    def form_valid(self, form):
        shift = form.save(commit=False)
        shift.employee = self.request.user

        shift.save()
        return super(ShiftManualCreate, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
class ShiftManualEdit(UpdateView, UserObjectOwnerMixin):
    model = Shift
    form_class = ShiftForm
    success_url = reverse_lazy('shift:list')
    template_name = 'shift/edit.html'

    def get_initial(self):
        """
        Sets initial data for the ModelForm, so we can use the user
        object and know which view created this form (UpdateView in
        this case)
        """
        return {
            'user': self.request.user,
            'view': 'shift_update',
        }


@method_decorator(login_required, name="dispatch")
class ShiftManualDelete(DeleteView, UserObjectOwnerMixin):
    model = Shift
    success_url = reverse_lazy('shift:list')
    template_name = 'shift/delete.html'


@method_decorator(login_required, name="dispatch")
class ShiftDayView(DayArchiveView):
    date_field = "shift_started"
    allow_future = False
    template_name = 'shift/day_archive_view.html'

    def get_queryset(self):
        return Shift.objects.filter(employee=self.request.user).order_by('shift_started')


@method_decorator(login_required, name="dispatch")
class ShiftWeekView(WeekArchiveView):
    date_field = "shift_started"
    week_format = "%W"
    allow_future = False
    template_name = 'shift/week_archive_view.html'

    def get_queryset(self):
        return Shift.objects.filter(employee=self.request.user).order_by('shift_started')


@method_decorator(login_required, name="dispatch")
class ShiftMonthView(MonthArchiveView):
    date_field = "shift_started"
    allow_empty = True
    allow_future = True
    template_name = 'shift/month_archive_view.html'

    class Meta:
        ordering = ["shift_started"]

    def get_queryset(self):
        return Shift.objects.filter(employee=self.request.user, shift_finished__isnull=False).order_by('shift_started')


@method_decorator(login_required, name="dispatch")
class ShiftYearView(YearArchiveView):
    date_field = "shift_started"
    allow_future = False
    template_name = 'shift/year_archive_view.html'

    def get_queryset(self):
        return Shift.objects.filter(employee=self.request.user).order_by('shift_started')
