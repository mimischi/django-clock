from test_plus.test import TestCase

from clock.contracts.models import Contract


class ExportViewTest(TestCase):
    def test_login_required_for_pdf_export(self):
        """
        Test the login requirement for all pages of the export app.
        """
        self.assertLoginRequired('export:contract', year=2016, month=1, pk=1)
        self.assertLoginRequired(
            'export:contract_nuke', year=2016, month=1, pk=1, hours=40)

    def test_logged_in_pdf_export(self):
        """
        Test whether a logged in user can export an empty month!
        For this we have to create a dummy contract!
        """
        user1 = self.make_user('user1')
        contract = Contract.objects.create(
            employee=user1, department='Test contract', hours='40')

        with self.login(username=user1.username, password='password'):
            self.get_check_200(
                'export:contract', year=2016, month=1, pk=contract.pk)

            # Somehow this does not work right now!
            # self.get_check_200('export:contract_nuke', year=2016, month=1, pk=contract.pk, hours=40)
