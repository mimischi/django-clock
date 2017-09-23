"""Test the Shift model"""
import pytest
from django.utils import timezone
from test_plus.test import TestCase

from clock.shifts.models import Shift


class ShiftTest(TestCase):
    def setUp(self):
        self.user = self.make_user()

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
