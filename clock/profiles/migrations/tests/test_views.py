from test_plus.test import TestCase


class ProfilesTestViews(TestCase):
    """
    Test views of profiles app.
    """

    def setUp(self):
        self.user1 = self.make_user()

    def test_profile_page(self):
        self.assertLoginRequired('profiles:account_view')
        self.assertLoginRequired('profiles:delete')

        # The goodbye page has no logic and will be shown to everyone who calls it.
        self.get('profiles:goodbye')

        with self.login(username=self.user1, password='password'):
            self.get_check_200('profiles:account_view')
            self.get_check_200('profiles:delete')
            self.get('profiles:goodbye')
