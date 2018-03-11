from test_plus.test import TestCase


class PagesViewTests(TestCase):
    """Tests the behaviour of the home view for guest users and authenticated
    users.

    """

    def setUp(self):
        self.user1 = self.make_user()

    def test_landing_page(self):
        """
        An unauthenticated user should see the normal landing page.
        """
        self.get_check_200('home')

        self.assertInContext('template_to_render')
        self.assertContext('template_to_render', 'pages/frontend/index.html')

    def test_dashboard(self):
        """
        Test two things:
            1) An authenticated user should see the dashboard.
            2) The context keys regarding contracts should be 'None'.
        """
        with self.login(username=self.user1, password='password'):
            self.get_check_200('home')

            self.assertInContext('template_to_render')
            self.assertContext('template_to_render',
                               'pages/backend/index.html')

            self.assertInContext('form')

            # The current user should not have any contracts/shifts yet
            self.assertInContext('all_contracts')
            self.assertContext('all_contracts', None)

            self.assertInContext('default_contract')
            self.assertContext('default_contract', None)

            self.assertInContext('last_shifts')
            self.assertContext('last_shifts', None)
