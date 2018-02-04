"""Test the Shift model"""
import pytest
from django.core.exceptions import ValidationError
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

    @freeze_time("2017-01-01 12:00:00")
    def test_shift_methods(self):
        start = timezone.now()
        stop = start + timezone.timedelta(0, 18000)

        shift = Shift(employee=self.user, started=start)

        # Check default values for freshly started shift
        assert not shift.is_finished
        assert shift.contract_or_none is None

        # Test that we can set a contract
        shift.contract = self.contract
        assert shift.contract_or_none == self.contract.department

        assert isinstance(shift.current_duration, timezone.timedelta)
        assert shift.current_duration == timezone.now() - start

        shift.finished = stop
        shift.save()
        assert shift.is_finished
