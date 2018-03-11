from test_plus.test import TestCase


class ContractViewTest(TestCase):
    def setUp(self):
        self.user = self.make_user('user1')

    def test_login_required_for_contract_views(self):
        """
        Test the login requirement for all pages of the contract app.
        """
        self.assertLoginRequired('contract:list')
        self.assertLoginRequired('contract:new')
        self.assertLoginRequired('contract:edit', pk=1)
        self.assertLoginRequired('contract:delete', pk=1)

    def test_logged_in_contract_views(self):
        """
        Test whether a logged in user can access all pages of contracts app.
        Edit/delete pages should NOT work if the object is not found!
        """

        self.assertLoginRequired('contract:list')

        with self.login(username=self.user.username, password='password'):
            self.get_check_200('contract:list')
            self.get_check_200('contract:new')

            edit = self.get('contract:edit', pk=1)
            self.response_404(edit)

            delete = self.get('contract:delete', pk=1)
            self.response_404(delete)
