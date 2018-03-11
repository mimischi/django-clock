"""Test the Shift forms"""
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from django.utils import timezone
from test_plus.test import RequestFactory, TestCase

from clock.shifts.forms import ShiftForm
from clock.shifts.models import Shift


class ShiftFormTest(TestCase):
    """Test ShiftForm for correct behavior."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = self.make_user()

    def setup_request(self, request):
        """Manage requests and setup session middleware."""
        request.user = self.user

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

    def test_form_valid_wo_pause(self):
        """Test that our form is valid without a pause."""
        url = reverse('shift:new')
        request = self.factory.get(url)
        self.setup_request(request)

        start = timezone.now() - timezone.timedelta(0, 3600)
        stop = timezone.now()
        pause = timezone.timedelta(0, 0)

        data = {
            'shift_started': start,
            'shift_finished': stop,
            'pause_duration': pause,
            'contract': None,
            'key': '',
            'tags': '',
            'note': '',
        }
        kwargs = {
            'view': 'shift_create',
            'request': request,
            'contract': None,
        }
        form = ShiftForm(data=data, **kwargs)
        assert form.is_valid()

    def test_form_valid_w_pause(self):
        """Test that our form is valid with a pause."""
        url = reverse('shift:new')
        request = self.factory.get(url)
        self.setup_request(request)

        start = timezone.now() - timezone.timedelta(0, 3600)
        stop = timezone.now()
        pause = '00:10'

        data = {
            'shift_started': start,
            'shift_finished': stop,
            'pause_duration': pause,
            'contract': None,
            'key': '',
            'tags': '',
            'note': '',
        }
        kwargs = {
            'view': 'shift_create',
            'request': request,
            'contract': None,
        }
        form = ShiftForm(data=data, **kwargs)
        assert form.is_valid()

    def test_form_not_valid_w_pause(self):
        """
        Test that our form is not valid with a pause bigger than the actual
        shift.
        """
        url = reverse('shift:new')
        request = self.factory.get(url)
        self.setup_request(request)

        start = timezone.now() - timezone.timedelta(0, 3600)
        stop = timezone.now()
        pause = timezone.timedelta(0, 3601)

        data = {
            'shift_started': start,
            'shift_finished': stop,
            'pause_duration': pause,
            'contract': None,
            'key': '',
            'tags': '',
            'note': '',
        }
        kwargs = {
            'view': 'shift_create',
            'request': request,
            'contract': None,
        }
        form = ShiftForm(data=data, **kwargs)
        assert not form.is_valid()

    def test_form_update_shift_instance(self):
        """
        Test that our form updates the shift instance correctly.
        """

        start = timezone.now() - timezone.timedelta(0, 18000)
        stop = timezone.now()
        pause = timezone.timedelta(0, 1800)

        shift = Shift.objects.create(
            employee=self.user,
            shift_started=start,
            shift_finished=stop,
            pause_duration=pause,
            bool_finished=True)

        url = reverse('shift:edit', kwargs={'pk': shift.pk})
        request = self.factory.get(url)
        self.setup_request(request)

        # The user input is defined in "%HH:%mm", so the duration is set to
        # "00:50", which here translated to 50 minutes.
        data = {
            'shift_started': start,
            'shift_finished': stop,
            'pause_duration': '00:50',
            'contract': None,
            'key': '',
            'tags': '',
            'note': '',
        }
        kwargs = {
            'view': 'shift_update',
            'request': request,
            'contract': None,
        }
        form = ShiftForm(data=data, instance=shift, **kwargs)
        assert form.is_valid()
        form.save()

        shift = Shift.objects.get(pk=shift.pk)
        assert shift.shift_duration == timezone.timedelta(0, 15000)
