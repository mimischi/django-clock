"""Test the utils module"""
from django.utils import timezone

from clock.pages.utils import round_time


def test_round_down():
    """Assert that the function rounds down to the nearest five minutes."""
    time = timezone.datetime(2017, 1, 1, 12, 2)
    assert round_time(dt=time) == timezone.datetime(2017, 1, 1, 12, 0)

    # We deliberately do not want to consider microseconds in our rounding
    # function
    time = timezone.datetime(2017, 1, 1, 12, 2, 29, 999999)
    assert round_time(dt=time) == timezone.datetime(2017, 1, 1, 12, 0)

    time = timezone.datetime(2017, 1, 1, 12, 4)
    assert round_time(dt=time, to="down") == timezone.datetime(2017, 1, 1, 12, 0)


def test_round_up():
    """Assert that the function rounds up to the nearest five minutes."""
    time = timezone.datetime(2017, 1, 1, 12, 3)
    assert round_time(dt=time) == timezone.datetime(2017, 1, 1, 12, 5)

    time = timezone.datetime(2017, 1, 1, 12, 2, 30)
    assert round_time(dt=time) == timezone.datetime(2017, 1, 1, 12, 5)

    time = timezone.datetime(2017, 1, 1, 12, 2)
    assert round_time(dt=time, to="up") == timezone.datetime(2017, 1, 1, 12, 5)
