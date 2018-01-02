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

    def test_form_update_shift_instance(self):
        """
        Test that our form updates the shift instance correctly.
        """

        start = timezone.now() - timezone.timedelta(0, 18000)
        stop = timezone.now()

        shift = Shift.objects.create(
            employee=self.user, started=start, finished=stop
        )

        url = reverse('shift:edit', kwargs={'pk': shift.pk})
        request = self.factory.get(url)
        self.setup_request(request)

        # The user input is defined in "%HH:%mm", so the duration is set to
        # "00:50", which here translated to 50 minutes.
        data = {
            'started': start,
            'finished': stop,
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
        assert shift.duration == timezone.timedelta(0, 18000)
