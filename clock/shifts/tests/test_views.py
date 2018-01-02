"""Test shift app views.

All messages are tested for the default English strings.
"""
from django.contrib.messages import get_messages
from django.utils import timezone, translation
from test_plus.test import TestCase

from clock.contracts.models import Contract
from clock.shifts.models import Shift


class ManualShiftViewTest(TestCase):
    """
    Test that the manual buttons for the shift views are working as intended.
    """

    def setUp(self):
        self.user = self.make_user()
        self.contract1 = Contract.objects.create(
            employee=self.user, department='Test department', hours='50')

    def test_manual_shift_start(self):
        """Assert that we can start a shift when logged in and without having a
        current shift.
        """
        with self.login(username=self.user.username, password='password'):
            response = self.post(
                'shift:quick_action',
                data={
                    '_start': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})

        with translation.override('en'):
            messages = [msg for msg in get_messages(response.wsgi_request)]

        shift = Shift.objects.all()[0]
        self.assertFalse(shift.bool_finished)
        self.assertIsNone(shift.finished)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].__str__(), 'Your shift has started!')

    def test_cannot_start_another_shift(self):
        """Assert that we cannot have two shifts running at the same time."""
        with self.login(username=self.user.username, password='password'):
            self.post(
                'shift:quick_action',
                data={
                    '_start': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})
            response2 = self.post(
                'shift:quick_action',
                data={
                    '_start': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})

        messages = [msg for msg in get_messages(response2.wsgi_request)]

        shift = Shift.objects.all()[0]
        self.assertFalse(shift.bool_finished)
        self.assertIsNone(shift.finished)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].__str__(),
                         'You already have an active shift!')

    def test_start_pause_resume_shift(self):
        """
        Assert that we can start, pause and unpause a shift.
        """
        with self.login(username=self.user.username, password='password'):
            self.post(
                'shift:quick_action',
                data={
                    '_start': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})
            response2 = self.post(
                'shift:quick_action',
                data={
                    '_pause': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})

            messages = [msg for msg in get_messages(response2.wsgi_request)]

            shift = Shift.objects.all()[0]
            self.assertFalse(shift.bool_finished)
            self.assertIsNone(shift.finished)
            self.assertTrue(shift.is_paused)

            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0].__str__(), 'Your shift was paused.')

            response3 = self.post(
                'shift:quick_action',
                data={
                    '_pause': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})

            messages = [msg for msg in get_messages(response3.wsgi_request)]

            shift = Shift.objects.all()[0]
            self.assertFalse(shift.bool_finished)
            self.assertIsNone(shift.finished)
            self.assertFalse(shift.is_paused)

            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0].__str__(),
                             'Your shift was continued.')

    def test_start_stop_shift(self):
        """
        Assert that we can start and stop a shift.
        """
        with self.login(username=self.user.username, password='password'):
            self.post(
                'shift:quick_action',
                data={
                    '_start': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})
            response2 = self.post(
                'shift:quick_action',
                data={
                    '_stop': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})

            messages = [msg for msg in get_messages(response2.wsgi_request)]

            shift = Shift.objects.all()[0]
            self.assertTrue(shift.bool_finished)
            self.assertIsNotNone(shift.finished)
            self.assertFalse(shift.is_paused)

            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0].__str__(), 'Your shift has finished!')

    def test_start_pause_stop_shift(self):
        """
        Assert that we can start, pause and stop a shift.
        """
        with self.login(username=self.user.username, password='password'):
            self.post(
                'shift:quick_action',
                data={
                    '_start': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})
            response2 = self.post(
                'shift:quick_action',
                data={
                    '_pause': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})

            messages = [msg for msg in get_messages(response2.wsgi_request)]

            shift = Shift.objects.all()[0]
            self.assertFalse(shift.bool_finished)
            self.assertIsNone(shift.finished)
            self.assertTrue(shift.is_paused)

            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0].__str__(), 'Your shift was paused.')

            response3 = self.post(
                'shift:quick_action',
                data={
                    '_stop': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})

            messages = [msg for msg in get_messages(response3.wsgi_request)]

            shift = Shift.objects.all()[0]
            self.assertTrue(shift.bool_finished)
            self.assertIsNotNone(shift.finished)
            self.assertFalse(shift.is_paused)

            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0].__str__(), 'Your shift has finished!')

    def test_cannot_stop_pause_non_existent_shift(self):
        """
        Assert that we cannot stop or pause a non-existent shift.
        """
        with self.login(username=self.user.username, password='password'):
            response1 = self.post(
                'shift:quick_action',
                data={
                    '_stop': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})

            messages1 = [msg for msg in get_messages(response1.wsgi_request)]
            self.assertEqual(len(messages1), 1)
            self.assertEqual(
                messages1[0].__str__(),
                'You need an active shift to perform this action!')

            response2 = self.post(
                'shift:quick_action',
                data={
                    '_pause': True,
                },
                follow=True,
                extra={'HTTP_ACCEPT_LANGUAGE': 'en'})
            messages2 = [msg for msg in get_messages(response2.wsgi_request)]
            self.assertEqual(len(messages2), 1)
            self.assertEqual(
                messages2[0].__str__(),
                'You need an active shift to perform this action!')

        shift = Shift.objects.all()
        self.assertEqual(len(shift), 0)


class ShiftsViewTest(TestCase):
    """
    Test views of Shift app.
    """

    def setUp(self):
        self.user1 = self.make_user()
        self.contract1 = Contract.objects.create(
            employee=self.user1, department='Test department', hours='40')

    def test_login_required_for_shift_views(self):
        """
        Make sure the views of the app are only accessible while logged in.
        """
        # Test basic creation / deletion views
        self.assertLoginRequired('shift:list')
        self.assertLoginRequired('shift:new')
        self.assertLoginRequired('shift:edit', pk=1)
        self.assertLoginRequired('shift:delete', pk=1)

        # Test the other list views. Contract IDs used reflect non-existing
        # contracts!
        # self.assertLoginRequired(
        #     'shift:archive_day', year=2016, month=6, day=10)
        # self.assertLoginRequired('shift:archive_week', year=2016, week=10)
        self.assertLoginRequired(
            'shift:archive_month_numeric', year=2016, month=5)
        self.assertLoginRequired(
            'shift:archive_month_contract_numeric',
            year=2016,
            month=5,
            contract=0)
        self.assertLoginRequired('shift:article_year_archive', year=2016)

    def test_logged_in_shift_views(self):
        """
        Test whether a logged in user can access all pages of the shifts app.
        Edit/delete pages should NOT work if the object is not found!
        """
        user1 = self.make_user('user1')

        self.assertLoginRequired('shift:list')

        with self.login(username=user1.username, password='password'):
            # Test basic creation / deletion views
            self.get_check_200('shift:list')
            self.get_check_200('shift:new')

            edit = self.get('shift:edit', pk=1)
            self.response_404(edit)

            delete = self.get('shift:delete', pk=1)
            self.response_404(delete)

            # Test other list views. The template here is not working.
            # Therefore a 404 error is expected!
            # day = self.get('shift:archive_day', year=2016, month=5, day=1)
            # self.response_404(day)

            # self.get_check_200('shift:archive_week', year=2016, week=10)
            self.get_check_200(
                'shift:archive_month_numeric', year=2016, month=5)
            self.get_check_200(
                'shift:archive_month_contract_numeric',
                year=2016,
                month=5,
                contract=0)
            self.get_check_200('shift:article_year_archive', year=2016)

    def test_surf_shift_list_wo_date(self):
        """Assert that we can surf through the shift list without specifying the
           current month.
        """
        user1 = self.make_user('user1')

        now = timezone.now()
        shift = Shift.objects.create(
            employee=user1,
            started=now,
            finished=now + timezone.timedelta(0, 3600))
        shift.save()

        with self.login(username=user1.username, password='password'):
            # Go into the shift list, but do not define any month and let the
            # backend figure it out by itself
            self.get_check_200('shift:list')
            # Edit the just created shift
            self.get_check_200('shift:edit', pk=shift.pk)
            # Try to delete it.
            self.get_check_200('shift:delete', pk=shift.pk)

    def test_surf_shift_list_w_date(self):
        """Assert that we can surf through the shift list while specifying the
           current month.
        """
        user1 = self.make_user('user1')

        now = timezone.now()
        shift = Shift.objects.create(
            employee=user1,
            started=now,
            finished=now + timezone.timedelta(0, 3600))
        shift.save()

        with self.login(username=user1.username, password='password'):
            self.get_check_200(
                'shift:archive_month_numeric', year=now.year, month=now.month)
            self.get_check_200('shift:edit', pk=shift.pk)
            self.get_check_200('shift:delete', pk=shift.pk)

    def test_surf_shift_list_w_date_and_contract(self):
        """Assert that we can surf through the shift list while specifying the
           current month and a contract.
        """
        user1 = self.make_user('user1')
        contract = self.contract1

        now = timezone.now()
        shift = Shift.objects.create(
            employee=user1,
            started=now,
            finished=now + timezone.timedelta(0, 3600),
            contract=self.contract1)
        shift.save()

        with self.login(username=user1.username, password='password'):
            self.get_check_200(
                'shift:archive_month_contract_numeric',
                year=now.year,
                month=now.month,
                contract=contract.pk)
            self.get_check_200('shift:edit', pk=shift.pk)
            self.get_check_200('shift:delete', pk=shift.pk)
