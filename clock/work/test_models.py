from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.messages import constants as MSG
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.utils import timezone

from .models import Shift
from .forms import ShiftForm


class ShiftMethodsTest(TestCase):
    def setUp(self):
        """
        Create an employee, so we can have someone to validate our
        shift system.
        """
        user = get_user_model().objects.create(username='john', is_active=True)
        user.set_password('doe')
        user.save()

    def test_shift_start_in_future(self):
        employee = get_user_model().objects.get(username='john')
        shift = Shift(employee=employee, shift_started=timezone.now() + timedelta(hours=1))

        with self.assertRaises(ValidationError):
            shift.full_clean()

    def test_shift_end_in_future(self):
        employee = get_user_model().objects.get(username='john')
        shift = Shift(employee=employee, shift_started=timezone.now(), shift_finished=timezone.now() + timedelta(hours=1))

        with self.assertRaises(ValidationError):
            shift.full_clean()

    def test_shift_end_before_start(self):
        employee = get_user_model().objects.get(username='john')
        shift = Shift(employee=employee, shift_started=timezone.now(), shift_finished=timezone.now() - timedelta(hours=2))

        with self.assertRaises(ValidationError):
            shift.full_clean()

    def test_check_for_overlaps(self):
        """
        Check if custom method 'check_for_overlaps' inside our custom
        ShiftForm is working. It should return a list of all shifts that
        are overlapping with the current one we're trying to submit.
        """
        employee = get_user_model().objects.get(username='john')
        shift = Shift.objects.create(employee=employee, shift_started=timezone.now() - timedelta(hours=10), shift_finished=timezone.now())

        form = ShiftForm(initial={'user': employee, 'view': 'shift_create'})
        self.assertIsNotNone(
            form.check_for_overlaps(
                employee=employee,
                shift_started=timezone.now() - timedelta(hours=4),
                shift_finished=timezone.now() - timedelta(hours=2)
            )
        )

    def test_shifts_for_overlap(self):
        """
        Similar to 'test_check_for_overlaps', but will test the whole form
        validation, instead of only the method 'check_for_overlaps'.
        """
        employee = get_user_model().objects.get(username='john')
        shift = Shift.objects.create(employee=employee, shift_started=timezone.now() - timedelta(hours=10), shift_finished=timezone.now() - timedelta(hours=3))
        initial_data = {'user': employee, 'view': 'shift_create',}


        # Check for overlap between the Shift that was specified in
        # the variable 'shift'. Start and end of shift are comepletely
        # inside the other shift
        form_data1 = {
            'shift_started': timezone.now()-timedelta(hours=5),
            'shift_finished': timezone.now()-timedelta(hours=2),
            'pause_duration': timedelta(),
        }
        form1 = ShiftForm(data=form_data1, initial=initial_data)
        self.assertEqual(form1.is_valid(), False)


        # Same as above. Only end of shift is inside the other shift.
        form_data2 = {
            'shift_started': timezone.now()-timedelta(hours=20),
            'shift_finished': timezone.now()-timedelta(hours=5),
            'pause_duration': timedelta(),
        }
        form2 = ShiftForm(data=form_data2, initial=initial_data)
        self.assertEqual(form2.is_valid(), False)


        # Same as above-above. Only beginning of shift is
        # inside the other shift.
        form_data3 = {
            'shift_started': timezone.now()-timedelta(hours=4),
            'shift_finished': timezone.now(),
            'pause_duration': timedelta(),
        }
        form3 = ShiftForm(data=form_data3, initial=initial_data)
        self.assertEqual(form3.is_valid(), False)


        # Sanity check. Start and end before the other shift.
        form_data4 = {
            'shift_started': timezone.now() - timedelta(hours=100),
            'shift_finished': timezone.now() - timedelta(hours=50),
            'pause_duration': timedelta(),
        }
        form4 = ShiftForm(data=form_data4, initial=initial_data)
        self.assertEqual(form4.is_valid(), True)


        # Second sanity check. Start and end after the other shift.
        form_data5 = {
            'shift_started': timezone.now() - timedelta(hours=1),
            'shift_finished': timezone.now(),
            'pause_duration': timedelta(),
        }
        form5 = ShiftForm(data=form_data5, initial=initial_data)
        self.assertEqual(form5.is_valid(), True)


class ShiftPostTest(TestCase):
    def setUp(self):
        """
        Create an employee, so we can have someone to validate our
        shift system.
        """
        user = get_user_model().objects.create(username='john', is_active=True)
        user.set_password('doe')
        user.save()

        client = Client()

    def test_quick_action_shift_cases(self):
        """
        We're testing the quick-actions, that the view 'shift_action' is processing.
        Only logged in users can use those and we're testing them by looking
        for the level of the received message.
        """

        login = self.client.login(username='john', password='doe')
        # User should be logged in
        self.assertEqual(login, True)

        # Start shift, while no other shift was started yet.
        response = self.client.post('/shift/quick_action/', {'_start': ''}, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, MSG.SUCCESS)

        # Start shift again, while other shift is running.
        response = self.client.post('/shift/quick_action/', {'_start': ''}, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, MSG.ERROR)

        # Pause current running shift
        response = self.client.post('/shift/quick_action/', {'_pause': ''}, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, MSG.SUCCESS)

        # Un-Pause current running shift
        response = self.client.post('/shift/quick_action/', {'_pause': ''}, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, MSG.SUCCESS)

        # Stop current shift
        response = self.client.post('/shift/quick_action/', {'_stop': ''}, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, MSG.SUCCESS)

        # Try to pause a not running shift
        response = self.client.post('/shift/quick_action/', {'_pause': ''}, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, MSG.ERROR)

        # Try to stop a not running shift
        response = self.client.post('/shift/quick_action/', {'_stop': ''}, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, MSG.ERROR)

        # Stop a currently paused shift: start a shift, pause it
        # and then stop it.
        response = self.client.post('/shift/quick_action/', {'_start': ''}, follow=True)
        response2 = self.client.post('/shift/quick_action/', {'_pause': ''}, follow=True)
        response3 = self.client.post('/shift/quick_action/', {'_stop': ''}, follow=True)
        messages = list(response3.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, MSG.SUCCESS)
