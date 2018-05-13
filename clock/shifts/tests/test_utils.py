"""Tests for the shift utilities."""
import pytest
import pytz
from django.contrib.auth import get_user_model
from django.utils import timezone
from test_plus import TestCase

from clock.contracts.models import Contract
from clock.shifts.factories import ShiftFactory, UserFactory
from clock.shifts.forms import ShiftForm
from clock.shifts.models import Shift
from clock.shifts.utils import (
    get_current_shift,
    get_last_shifts,
    get_shifts_to_check_for_overlaps,
    sort_overlapping_shifts,
)


@pytest.fixture
@pytest.mark.django_db
def setup_shifts():
    user = UserFactory()
    contract = Contract.objects.create(
        employee=user, department='Test department', hours='50'
    )

    started = timezone.datetime(2018, 4, 1, 8, 30)
    finished = timezone.datetime(2018, 4, 1, 17, 0)
    end_date = timezone.datetime(2018, 6, 30)
    form = ShiftForm(
        data={
            'started': started,
            'finished': finished,
            'reoccuring': 'DAILY',
            'end_date': end_date,
            'employee': user,
            'contract': contract.pk
        },
        **{
            'user': user,
            'view': None
        }
    )
    form.save()


@pytest.fixture
def get_user():
    user = get_user_model()
    return user.objects.all()[0]


@pytest.fixture
def get_contract():
    return Contract.objects.all()[0]


@pytest.mark.django_db
def test_sort_overlapping_shifts(setup_shifts, get_user, get_contract):
    """Test that we sort the shifts into the overlapping ones."""
    started = timezone.make_aware(
        timezone.datetime(2018, 4, 1, 7), timezone=pytz.utc
    )
    finished = timezone.make_aware(
        timezone.datetime(2018, 4, 1, 10), timezone=pytz.utc
    )
    shifts = Shift.objects.filter(
        employee=get_user,
        contract=get_contract,
        started__lte=finished,
        finished__gte=started
    ).order_by('-created_at')

    good_shifts, bad_shifts = sort_overlapping_shifts(
        started, finished, get_user, get_contract, shifts
    )
    assert len(bad_shifts) == 1
    assert not good_shifts


@pytest.mark.django_db
def test_sort_overlapping_shifts_without_overlaps(
    setup_shifts, get_user, get_contract
):
    """Test that we correctly sort shifts into the non-overlapping ones."""
    started = timezone.make_aware(timezone.datetime(2018, 4, 1, 2))
    finished = timezone.make_aware(timezone.datetime(2018, 4, 1, 4))
    shifts = Shift.objects.filter(
        employee=get_user,
        contract=get_contract,
        started__lte=timezone.make_aware(timezone.datetime(2018, 4, 30)),
        finished__gte=timezone.make_aware(timezone.datetime(2018, 4, 1))
    ).order_by('-created_at')

    good_shifts, bad_shifts = sort_overlapping_shifts(
        started, finished, get_user, get_contract, shifts
    )
    assert not bad_shifts
    assert len(good_shifts) == 29

    for shift in good_shifts:
        assert shift.started.time() == started.astimezone(pytz.utc).time()
        assert shift.finished.time() == finished.astimezone(pytz.utc).time()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'start_date, end_date, count', [
        (
            timezone.datetime(2018, 4, 5, 6, 0),
            timezone.datetime(2018, 4, 5, 7, 55), 1
        ), (timezone.datetime(2018, 4, 5), timezone.datetime(2018, 4, 6), 2),
        (timezone.datetime(2018, 4, 5), timezone.datetime(2018, 4, 9), 5)
    ]
)
def test_retrieval_of_shifts_to_check_for_overlaps(
    setup_shifts, get_user, get_contract, start_date, end_date, count
):
    """Test that we retrieve the correct shifts to check for overlaps."""
    started = timezone.make_aware(start_date)
    finished = timezone.make_aware(end_date)
    reoccuring = 'DAILY'
    shifts = get_shifts_to_check_for_overlaps(
        started, finished, get_user, get_contract.pk, reoccuring
    )
    assert shifts.count() == count


@pytest.mark.django_db
def test_overlap_excludes_shift(setup_shifts, get_user, get_contract):
    """Test that we can exclude a shift from the overlap check."""
    started = timezone.datetime(2018, 4, 2, 6, 0)
    finished = timezone.datetime(2018, 4, 2, 8, 0)
    form = ShiftForm(
        data={
            'started': started,
            'finished': finished,
            'reoccuring': 'ONCE',
            'employee': get_user,
            'contract': get_contract.pk
        },
        **{
            'user': get_user,
            'view': None
        }
    )
    form.save()
    start_date = timezone.make_aware(timezone.datetime(2018, 4, 2))
    end_date = timezone.make_aware(timezone.datetime(2018, 4, 3))
    reoccuring = 'DAILY'
    shifts = get_shifts_to_check_for_overlaps(
        start_date,
        end_date,
        get_user,
        get_contract.pk,
        reoccuring,
        exclude_shift=form.instance.pk
    )
    assert shifts.count() == 2


class TestUtils(TestCase):
    """Test the functionality of the shift utilities."""

    def setUp(self):
        self.user = self.make_user()
        self.contract1 = Contract.objects.create(
            employee=self.user, department='Test department', hours='50'
        )

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
                if shift.finished == five_shifts[i + 1].finished:
                    continue
                self.assertTrue(shift.finished > five_shifts[i + 1].finished)
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
            self.assertIsNotNone(shift.finished)

    def test_retrieve_current_running_shift(self):
        """Test that we can retrieve the currently running shift."""

        no_shift = get_current_shift(self.user)
        self.assertIsNone(no_shift)

        with self.login(username=self.user.username, password='password'):
            self.post(
                'shift:quick_action', data={
                    '_start': True,
                }, follow=True
            )

            last_shift = get_current_shift(self.user)
            self.assertIsNotNone(last_shift)
            self.assertIsNone(last_shift.finished, '')
