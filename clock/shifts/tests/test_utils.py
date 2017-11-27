"""Tests for the shift utilities."""
from test_plus import TestCase

from clock.contracts.models import Contract
from clock.shifts.factories import ShiftFactory, UserFactory
from clock.shifts.models import Shift
from clock.shifts.utils import get_current_shift, get_last_shifts


class TestUtils(TestCase):
    """Test the functionality of the shift utilities."""

    def setUp(self):
        self.user = self.make_user()
        self.contract1 = Contract.objects.create(
            employee=self.user, department='Test department', hours='50')

    def test_get_last_shifts(self):
        employee = UserFactory()

        # Function returns `None` when user has no shifts yet
        no_shifts = get_last_shifts(employee)
        self.assertIsNone(no_shifts)

        # Function returns the last 5 shifts per default
        ShiftFactory.create_batch(10, employee=employee)
        five_shifts = get_last_shifts(employee)

        self.assertEqual(len(five_shifts), 5)
        self.assertIsInstance(five_shifts[0], Shift)
        self.assertEqual(five_shifts[0].employee, employee)

        # Assert we get the correct order, with the latest finished shift
        # first.
        for i, shift in enumerate(five_shifts):
            try:
                self.assertTrue(five_shifts[i].shift_finished >
                                five_shifts[i + 1].shift_finished)
            except IndexError:
                pass

        # Return seven shifts
        seven_shifts = get_last_shifts(employee, count=7)
        self.assertEqual(len(seven_shifts), 7)

        # Return the maximum number of shifts, even if more are requested
        eleven_shifts = get_last_shifts(employee, count=11)
        self.assertEqual(len(eleven_shifts), 10)

        # Make sure we only retrieve finished shifts
        for shift in eleven_shifts:
            self.assertIsNotNone(shift.shift_finished)

    def test_retrieve_current_running_shift(self):
        """Test that we can retrieve the currently running shift."""

        no_shift = get_current_shift(self.user)
        self.assertIsNone(no_shift)

        with self.login(username=self.user.username, password='password'):
            self.post(
                'shift:quick_action', data={
                    '_start': True,
                }, follow=True)

            last_shift = get_current_shift(self.user)
            self.assertIsNotNone(last_shift)
            self.assertIsNone(last_shift.shift_finished, '')
