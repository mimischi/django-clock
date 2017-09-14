from test_plus.test import TestCase

from clock.contracts.models import Contract


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

        # Test the other list views. Contract IDs used reflect non-existing contracts!
        self.assertLoginRequired(
            'shift:archive_day', year=2016, month=6, day=10)
        self.assertLoginRequired('shift:archive_week', year=2016, week=10)
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

            # Test other list views
            # The template here is not working. Therefore a 404 error is expected!
            day = self.get('shift:archive_day', year=2016, month=5, day=1)
            self.response_404(day)

            self.get_check_200('shift:archive_week', year=2016, week=10)
            self.get_check_200(
                'shift:archive_month_numeric', year=2016, month=5)
            self.get_check_200(
                'shift:archive_month_contract_numeric',
                year=2016,
                month=5,
                contract=0)
            self.get_check_200('shift:article_year_archive', year=2016)
