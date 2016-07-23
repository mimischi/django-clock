from test_plus.test import TestCase


class ContactViewTests(TestCase):
    def test_contact_page(self):
        response = self.get_check_200('contact:form')

    def test_contact_success_page(self):
        response = self.get_check_200('contact:success')
