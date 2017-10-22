"""Test the Shift model"""
import pytest
from django.utils import timezone
from freezegun import freeze_time
from test_plus.test import TestCase

from clock.contracts.models import Contract
from clock.shifts.models import Shift


class ShiftTest(TestCase):
    def setUp(self):
        self.user = self.make_user()
        self.contract = Contract.objects.create(
            department='Test', employee=self.user, hours=40)

    def test_shift_duration_one_hour(self):
        """Check that the shift length is 1 hour."""
        start = timezone.now()
        stop = start + timezone.timedelta(0, 3600)

        shift = Shift.objects.create(
            employee=self.user,
            shift_started=start,
            shift_finished=stop,
            bool_finished=True)

        assert shift.shift_duration == timezone.timedelta(0, 3600)

    def test_shift_duration_rounding(self):
        """
        Check that the rounding of shift start / finished times actually works as
        intended. We expect it to round to the closest 5 minutes.
        """

        # Finish 12 minutes later. Total duration should be 10 minutes
        start1 = timezone.make_aware(timezone.datetime(2017, 1, 1, 12, 0))
        stop1 = start1 + timezone.timedelta(0, 720)

        shift1 = Shift.objects.create(
            employee=self.user,
            shift_started=start1,
            shift_finished=stop1,
            bool_finished=True)

        assert shift1.shift_duration == timezone.timedelta(0, 600)

        # Finish 8 minutes later. Total duration should be 10 minutes.
        start2 = timezone.make_aware(timezone.datetime(2017, 1, 1, 12, 0))
        stop2 = start2 + timezone.timedelta(0, 480)

        shift2 = Shift.objects.create(
            employee=self.user,
            shift_started=start2,
            shift_finished=stop2,
            bool_finished=True)

        assert shift2.shift_duration == timezone.timedelta(0, 600)

        # Finish 13 minutes later. Total duration should be 15 minutes.
        start3 = timezone.make_aware(timezone.datetime(2017, 1, 1, 12, 0))
        stop3 = start3 + timezone.timedelta(0, 780)

        shift3 = Shift.objects.create(
            employee=self.user,
            shift_started=start3,
            shift_finished=stop3,
            bool_finished=True)

        assert shift3.shift_duration == timezone.timedelta(0, 900)

    def test_minimum_shift_length(self):
        """Make sure that the minimum shift length is 5 minutes."""
        start = timezone.now()
        stop = start + timezone.timedelta(0, 60)

        shift = Shift.objects.create(
            employee=self.user,
            shift_started=start,
            shift_finished=stop,
            bool_finished=True)

        assert shift.shift_duration == timezone.timedelta(0, 300)

    def test_pause_time(self):
        """
        Assert that the pause time is correctly used. The pause time should be
        rounded to the nearest 5 minutes.
        """
        start = timezone.now()
        stop = start + timezone.timedelta(0, 3600)
        pause = timezone.timedelta(0, 500)

        shift = Shift.objects.create(
            employee=self.user,
            shift_started=start,
            shift_finished=stop,
            pause_duration=pause,
            bool_finished=True)

        assert shift.shift_duration == timezone.timedelta(0, 3000)

    def test_update_pause_duration(self):
        """
        Make sure that we can update the pause duration and calculate
        the new total shift duration correctly.
        """

        start = timezone.now()
        stop = start + timezone.timedelta(0, 18000)
        pause = timezone.timedelta(0, 3000)

        shift = Shift.objects.create(
            employee=self.user,
            shift_started=start,
            shift_finished=stop,
            pause_duration=pause,
            bool_finished=True)

        assert shift.shift_duration == timezone.timedelta(0, 15000)
        assert shift.pause_duration == pause

        new_pause = timezone.timedelta(0, 1500)
        shift.pause_duration = new_pause
        shift.save()

        assert shift.pause_duration == new_pause
        assert shift.shift_duration == timezone.timedelta(0, 16500)

    @freeze_time("2017-01-01 12:00:00")
    def test_shift_methods(self):
        start = timezone.now()
        stop = start + timezone.timedelta(0, 18000)
        pause = timezone.timedelta(0, 3000)

        shift = Shift(
            employee=self.user,
            shift_started=start,
            shift_finished=stop, )

        # Check default values for freshly started shift
        assert not shift.is_finished
        assert not shift.is_paused
        assert not shift.is_shift_currently_paused()
        # TODO: This is aweful! We should return `None` instead of `str(None)`
        assert shift.contract_or_none == 'None'

        shift.contract = self.contract
        assert shift.contract_or_none == self.contract.department

        # TODO: Same thing.. return `None`!
        assert shift.pause_start_end == '-'
        shift.pause_duration = pause
        assert shift.pause_start_end == '16:10 - 17:00'

        # Pause shift
        shift.pause()
        assert isinstance(shift.pause_started, timezone.datetime)
        assert shift.is_paused

        assert isinstance(shift.total_pause_time, timezone.timedelta)
        assert shift.total_pause_time == pause

        # Unpause shift
        shift.unpause()
        assert isinstance(shift.pause_duration, timezone.timedelta)
        assert not shift.pause_started
        assert isinstance(shift.total_pause_time, timezone.timedelta)
        assert shift.total_pause_time == pause

        # Toggle pause / unpause
        shift.toggle_pause()
        assert shift.is_paused
        shift.toggle_pause()
        assert not shift.is_paused

        assert isinstance(shift.current_duration, timezone.timedelta)
        assert shift.current_duration == timezone.now() - start - pause

        shift.shift_finished = stop
        shift.bool_finished = True
        assert shift.is_finished
