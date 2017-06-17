"""Factories for Shifts."""
import factory
from django.utils import timezone

from clock.shifts.models import Shift
from clock.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('first_name')


class ShiftFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shift

    shift_started = factory.Faker(
        'date_time_between',
        start_date='-20h',
        end_date='-10h',
        tzinfo=timezone.get_current_timezone())
    shift_finished = factory.Faker(
        'date_time_between',
        start_date='-9h',
        end_date='now',
        tzinfo=timezone.get_current_timezone())
    employee = factory.SubFactory(UserFactory)
