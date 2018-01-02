"""Test the Shift model"""
from django.utils import timezone
from freezegun import freeze_time
from test_plus.test import TestCase

from clock.contracts.models import Contract
from clock.shifts.models import Shift


class ShiftTest(TestCase):
    def setUp(self):
        self.user = self.make_user()
        self.contract = Contract.objects.create(
            department='Test', employee=self.user, hours=40
        )

    def test_shift_duration_one_hour(self):
        """Check that the shift length is 1 hour."""
        start = timezone.now()
        stop = start + timezone.timedelta(0, 3600)

        shift = Shift.objects.create(
            employee=self.user, started=start, finished=stop
        )

        assert shift.duration == timezone.timedelta(0, 3600)

    def test_shift_duration_rounding(self):
        """Check that the rounding of shift start / finished times actually works as
        intended. We expect it to round to the closest 5 minutes.
        """

        # Finish 12 minutes later. Total duration should be 10 minutes
        start1 = timezone.make_aware(timezone.datetime(2017, 1, 1, 12, 0))
        stop1 = start1 + timezone.timedelta(0, 720)

        shift1 = Shift.objects.create(
            employee=self.user, started=start1, finished=stop1
        )

        assert shift1.duration == timezone.timedelta(0, 600)

        # Finish 8 minutes later. Total duration should be 10 minutes.
        start2 = timezone.make_aware(timezone.datetime(2017, 1, 1, 12, 0))
        stop2 = start2 + timezone.timedelta(0, 480)

        shift2 = Shift.objects.create(
            employee=self.user, started=start2, finished=stop2
        )

        assert shift2.duration == timezone.timedelta(0, 600)

        # Finish 13 minutes later. Total duration should be 15 minutes.
        start3 = timezone.make_aware(timezone.datetime(2017, 1, 1, 12, 0))
        stop3 = start3 + timezone.timedelta(0, 780)

        shift3 = Shift.objects.create(
            employee=self.user, started=start3, finished=stop3
        )

        assert shift3.duration == timezone.timedelta(0, 900)

    def test_minimum_shift_length(self):
        """Make sure that the minimum shift length is 5 minutes."""
        start = timezone.now()
        stop = start + timezone.timedelta(0, 60)

        shift = Shift.objects.create(
            employee=self.user, started=start, finished=stop
        )

        assert shift.duration == timezone.timedelta(0, 300)

    @freeze_time("2017-01-01 12:00:00")
    def test_shift_methods(self):
        start = timezone.now()
        stop = start + timezone.timedelta(0, 18000)

        shift = Shift(employee=self.user, started=start)

        # Check default values for freshly started shift
        assert not shift.is_finished
        assert shift.contract_or_none is None

        shift.contract = self.contract
        assert shift.contract_or_none == self.contract.department

        assert isinstance(shift.current_duration, timezone.timedelta)
        assert shift.current_duration == timezone.now() - start

        shift.finished = stop
        assert shift.is_finished
