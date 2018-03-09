"""Test the Shift forms"""
from datetime import timedelta

import pytz
from django import forms
from django.utils import timezone
from freezegun import freeze_time
from test_plus.test import TestCase

from clock.contracts.models import Contract
from clock.shifts.forms import ClockInForm, ClockOutForm, ShiftForm
from clock.shifts.models import Shift


def dt_wrapper(dt):
    """Wrapper to make naive datetime aware."""

    return timezone.make_aware(dt, timezone=pytz.timezone('UTC'))


class ClockInOutFormTest(TestCase):
    """Test the ClockInForm and ClockOutForm."""

    def setUp(self):
        self.user = self.make_user()
        self.contract = Contract.objects.create(
            employee=self.user, hours=300, department='Test'
        )

    def test_clock_in(self):
        """Test that we can clock in as expected."""
        with freeze_time('2018-03-01 09:02'):
            # Test that we can clock in
            form = ClockInForm(
                data={'started': timezone.now(),
                      'contract': self.contract.pk},
                user=self.user
            )
            assert form.is_valid()
            form.clock_in()

            # Test that we cannot start another shift, while one is already
            # clocked-in.
            form = ClockInForm(
                data={'started': timezone.now(),
                      'contract': self.contract.pk},
                user=self.user
            )
            assert not form.is_valid()
            assert form.errors['__all__'] == [
                'You cannot clock into two shifts at once!'
            ]
            assert form.cleaned_data.get('started') == dt_wrapper(
                timezone.datetime(2018, 3, 1, 9, 2),
            )

    def test_clock_out(self):
        """Test that we can clock out as expected."""
        # Test that we cannot clock-out, if there is no running shift.
        form = ClockOutForm(data={'finished': timezone.now()}, instance=None)
        assert not form.is_valid()
        assert form.errors['__all__'] == [
            'You cannot clock out of a non-existent shift!'
        ]

        # Test that the shift will be deleted automatically, if it is shorter
        # than five minutes.
        with freeze_time('2018-03-01 09:20'):
            form_in = ClockInForm(
                data={'started': timezone.now(),
                      'contract': self.contract.pk},
                user=self.user
            )
            assert form_in.is_valid()
            form_in.clock_in()

            shift = Shift.objects.get(
                employee=self.user, finished__isnull=True
            )
            form_out = ClockOutForm(
                data={
                    'finished': timezone.now() + timezone.timedelta(minutes=2)
                },
                instance=shift
            )
            assert not form_out.is_valid()
            assert form_out.errors['__all__'] == [
                'A shift cannot be shorter than 5 minutes. We deleted it for you :)'
            ]
            assert Shift.objects.filter(pk=shift.pk).count() == 0

        # Test that we can clock out of a shift, if it is longer than five minutes.
        # Also test that it gets rounded correctly.
        with freeze_time('2018-03-01 09:22'):
            form_in = ClockInForm(
                data={'started': timezone.now(),
                      'contract': self.contract.pk},
                user=self.user
            )
            assert form_in.is_valid()
            form_in.clock_in()

            shift = Shift.objects.get(
                employee=self.user, finished__isnull=True
            )
            form_out = ClockOutForm(
                data={
                    'finished': timezone.now() + timezone.timedelta(minutes=6)
                },
                instance=shift
            )
            assert form_out.is_valid()
            assert form_out.instance.started == timezone.make_aware(
                timezone.datetime(2018, 3, 1, 9, 20),
                timezone=pytz.timezone('UTC')
            )
            assert form_out.cleaned_data.get('finished'
                                             ) == timezone.make_aware(
                                                 timezone.datetime(
                                                     2018, 3, 1, 9, 30
                                                 ),
                                                 timezone=pytz.timezone('UTC')
                                             )
            assert form_out.instance.duration == timezone.timedelta(minutes=10)

    def test_split_shifts(self):
        """Test that shifts spanning over two days are split at midnight."""
        with freeze_time("2017-01-01 18:00"):
            form = ClockInForm(
                data={'started': timezone.now(),
                      'contract': self.contract.pk},
                user=self.user
            )
            assert form.is_valid()
            form.clock_in()

        with freeze_time("2017-01-02 02:00"):
            shift = Shift.objects.get(
                employee=self.user, finished__isnull=True
            )
            form_out = ClockOutForm(
                data={'finished': timezone.now()}, instance=shift
            )
            assert form_out.is_valid()
            form_out.clock_out()
            assert form_out.instance.duration == timedelta(0, 21300)

            new_shift = Shift.objects.get(
                employee=self.user,
                started=dt_wrapper(timezone.datetime(2017, 1, 2, 0, 0))
            )
            assert new_shift.started == dt_wrapper(
                timezone.datetime(2017, 1, 2, 0, 0)
            )
            assert new_shift.finished == dt_wrapper(
                timezone.datetime(2017, 1, 2, 2, 0)
            )
            assert new_shift.duration == timedelta(0, 7200)

    def test_split_shifts_that_are_too_short(self):
        """Test that we handle shifts that are too short after splitting correctly."""

        # Make sure we do not create a new shift that is too short
        with freeze_time("2017-01-01 23:00"):
            form = ClockInForm(
                data={'started': timezone.now(),
                      'contract': self.contract.pk},
                user=self.user
            )
            assert form.is_valid()
            form.clock_in()

        with freeze_time("2017-01-02 00:02"):
            shift = Shift.objects.get(
                employee=self.user, finished__isnull=True
            )
            form_out = ClockOutForm(
                data={'finished': timezone.now()}, instance=shift
            )
            assert form_out.is_valid()
            form_out.clock_out()

            new_shift = Shift.objects.filter(
                employee=self.user,
                started=dt_wrapper(timezone.datetime(2017, 1, 2, 0, 0))
            ).count()
            assert new_shift == 0

        # Make sure we do not create any shift if both ends are too short.
        with freeze_time("2017-01-01 23:58"):
            form = ClockInForm(
                data={'started': timezone.now(),
                      'contract': self.contract.pk},
                user=self.user
            )
            assert form.is_valid()
            form.clock_in()

        with freeze_time("2017-01-02 00:02"):
            shift = Shift.objects.get(
                employee=self.user, finished__isnull=True
            )
            form_out = ClockOutForm(
                data={'finished': timezone.now()}, instance=shift
            )
            assert form_out.is_valid()
            form_out.clock_out()

            old_shift = Shift.objects.filter(pk=shift.pk).count()
            assert old_shift == 0
            new_shift = Shift.objects.filter(
                employee=self.user,
                started=dt_wrapper(timezone.datetime(2017, 1, 2, 0, 0))
            ).count()
            assert new_shift == 0

        # Make sure we only delete the first splitted Shift, but create the second.
        with freeze_time("2017-01-01 23:58"):
            form = ClockInForm(
                data={'started': timezone.now(),
                      'contract': self.contract.pk},
                user=self.user
            )
            assert form.is_valid()
            form.clock_in()

        with freeze_time("2017-01-02 00:05"):
            shift = Shift.objects.get(
                employee=self.user, finished__isnull=True
            )
            form_out = ClockOutForm(
                data={'finished': timezone.now()}, instance=shift
            )
            assert form_out.is_valid()
            form_out.clock_out()

            # Make sure the old shift that was too short was deleted!
            old_shift = Shift.objects.filter(pk=shift.pk).count()
            assert old_shift == 0
            new_shift = Shift.objects.filter(
                employee=self.user,
                started=dt_wrapper(timezone.datetime(2017, 1, 2, 0, 0))
            ).count()
            assert new_shift == 1

        # Make sure that a short new shift of 5 minutes on the next day works.
        with freeze_time("2017-01-01 23:00"):
            form = ClockInForm(
                data={'started': timezone.now(),
                      'contract': self.contract.pk},
                user=self.user
            )
            assert form.is_valid()
            form.clock_in()

        with freeze_time("2017-01-02 00:03"):
            shift = Shift.objects.get(
                employee=self.user, finished__isnull=True
            )
            form_out = ClockOutForm(
                data={'finished': timezone.now()}, instance=shift
            )
            assert form_out.is_valid()
            form_out.clock_out()

            new_shift = Shift.objects.filter(
                employee=self.user,
                started=dt_wrapper(timezone.datetime(2017, 1, 2, 0, 0))
            ).count()
            assert new_shift == 2


class ShiftFormTest(TestCase):
    """Test ShiftForm for correct behavior."""

    def setUp(self):
        self.user = self.make_user()
        self.contract = Contract.objects.create(
            employee=self.user, hours=40, department='Goethe'
        )
        self.contract2 = Contract.objects.create(
            employee=self.user, hours=20, department='Goethe2'
        )

    def prepare_form(
        self,
        obj,
        started=None,
        finished=None,
        employee=None,
        contract=None,
        instance=None,
        view=None,
        kwargs=None
    ):
        if not kwargs:
            kwargs = {'view': view, 'contract': contract, 'user': self.user}

        data = {'contract': contract, 'reoccuring': 'ONCE'}
        for arg in ['employee', 'started', 'finished']:
            if eval(arg):
                data[arg] = eval(arg)

        form = obj(data=data, instance=instance, **kwargs)
        return form

    def work_time_tests(self, form, minutes, too_long=True):
        work_time = form.work_time_current_day()
        assert work_time == timezone.timedelta(minutes=minutes)
        if too_long:
            assert not form.is_too_long()
            assert not form.is_too_long(worked_hours=work_time)
        else:
            assert form.is_too_long()
            assert form.is_too_long(worked_hours=work_time)

    def test_can_create_shift_with_form(self):
        """Test that we can create a new shift with the ShiftForm."""
        start = timezone.datetime(2018, 1, 1, 8, 0)
        stop = timezone.datetime(2018, 1, 1, 10, 0)

        form = self.prepare_form(ShiftForm, start, stop, self.user)
        form.is_valid()
        assert form.is_valid()
        assert form.instance.started == timezone.make_aware(start)
        assert form.instance.finished == timezone.make_aware(stop)
        assert form.instance.duration == timezone.timedelta(minutes=120)

        # Test output of the `work_time_current_day` method
        self.work_time_tests(form, minutes=0)

    def test_shift_time_constencies(self):
        """Test a few cases for consistency.

        * Make sue that the start time is smaller than the finish time.
        * Make sure that we cannot save a shift that is shorter than 5 minutes.
        """
        start = timezone.datetime(2018, 1, 1, 9, 0)
        stop = timezone.datetime(2018, 1, 1, 8, 0)
        form = self.prepare_form(ShiftForm, start, stop, self.user)
        assert not form.is_valid()
        error = form.errors['__all__'][0]
        assert error == 'The shift cannot start after finishing.'

        start = timezone.datetime(2018, 1, 1, 8, 0)
        stop = timezone.datetime(2018, 1, 1, 8, 2)
        form = self.prepare_form(ShiftForm, start, stop, self.user)
        assert not form.is_valid()
        error = form.errors['__all__'][0]
        assert error == 'We cannot save a shift that is this short.'

    def test_form_update_shift_instance(self):
        """
        Test that our form updates the shift instance correctly.
        """

        start = timezone.datetime(2018, 1, 1, 8, 0)
        stop = timezone.datetime(2018, 1, 1, 10, 0)
        initial_form = self.prepare_form(ShiftForm, start, stop, self.user)
        initial_form.save()
        assert initial_form.instance.duration == timezone.timedelta(
            minutes=120
        )

        form = self.prepare_form(
            ShiftForm,
            start,
            stop + timezone.timedelta(minutes=5),
            self.user,
            instance=initial_form.instance
        )
        assert form.is_valid()
        form.save()
        assert 'finished' in form.changed_data
        assert form.instance.duration == timezone.timedelta(minutes=125)

    def test_overlaps(self):
        """Test that we detect overlaps correctly."""
        # First save some Shift without any contract
        start = timezone.datetime(2018, 1, 1, 8, 0)
        stop = timezone.datetime(2018, 1, 1, 10, 0)
        initial_form = self.prepare_form(ShiftForm, start, stop, self.user)
        initial_form.save()

        # Now save a shift with a contract. This should not produce any
        # collisions.
        start = timezone.datetime(2018, 1, 1, 7, 0)
        stop = timezone.datetime(2018, 1, 1, 11, 0)
        form = ShiftForm(
            data={
                'started': start,
                'finished': stop,
                'reoccuring': 'ONCE',
                'employee': self.user,
                'contract': self.contract.pk
            },
            **{'user': self.user,
               'view': None}
        )
        assert form.is_valid()
        assert len(form.check_for_overlaps) == 0
        form.save()

        # Now try to save another Shift in the same contract. This should
        # produce an error!
        start = timezone.datetime(2018, 1, 1, 4, 0)
        stop = timezone.datetime(2018, 1, 1, 11, 0)
        form = ShiftForm(
            data={
                'started': start,
                'finished': stop,
                'reoccuring': 'ONCE',
                'employee': self.user,
                'contract': self.contract.pk
            },
            **{'user': self.user,
               'view': None}
        )
        assert not form.is_valid()
        assert len(form.check_for_overlaps) == 1

        # Now try to save another Shift in a different contract. This should
        # produce an error!
        start = timezone.datetime(2018, 1, 1, 4, 0)
        stop = timezone.datetime(2018, 1, 1, 11, 0)
        form = ShiftForm(
            data={
                'started': start,
                'finished': stop,
                'reoccuring': 'ONCE',
                'employee': self.user,
                'contract': self.contract2.pk
            },
            **{'user': self.user,
               'view': None}
        )
        assert not form.is_valid()
        assert len(form.check_for_overlaps) == 1

        # Check that we can save another shift without any contract.
        start = timezone.datetime(2018, 1, 1, 6, 0)
        stop = timezone.datetime(2018, 1, 1, 11, 0)
        initial_form = self.prepare_form(ShiftForm, start, stop, self.user)
        assert initial_form.is_valid()
        assert initial_form.check_for_overlaps is None
