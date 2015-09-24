from datetime import timedelta

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from allauth.account.adapter import DefaultAccountAdapter

from work.models import Shift

# class ShiftTest(TestCase):

#     def createEmployee(self):
#         return DefaultAccountAdapter.new_user()

#     def test_shift_for_no_overlap(self):
#         shift1 = Shift.objects.create(employee=createEmployee(), shift_started=timezone.now() - timedelta(hours=2), shift_finished=timezone.now() - timedelta(hours=2))
#         shift2 = Shift.objects.create(employee=createEmployee(), shift_started=timezone.now() - timedelta(hours=1), shift_finished=(timezone.now()))

#         self.assertEqual(shift2.shift_time_validation(), False)
