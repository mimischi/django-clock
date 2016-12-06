from test_plus.test import TestCase

from clock.contracts.models import Contract


class ContractTestCase(TestCase):
    """
    Tests the contract behaviour.
    """

    def setUp(self):
        self.user1 = self.make_user(username='user1')
        self.contract1 = Contract.objects.create(employee=self.user1, department='Test contract', hours='40')

    def test__unicode__(self):
        self.assertEqual(self.contract1.__unicode__(), 'Test contract')
