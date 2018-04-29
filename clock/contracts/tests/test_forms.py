"""Test the Contract forms."""
from test_plus.test import TestCase

from clock.contracts.forms import ContractForm


class ContractFormTest(TestCase):
    """Test the ContractForm."""

    def setUp(self):
        self.user = self.make_user()

    def test_can_create_contract_without_start_end_date(self):
        form = ContractForm(
            data={
                'department': 'GU',
                'hours': 20
            }, user=self.user
        )
        assert form.is_valid()
        assert form.cleaned_data['hours'] == '20:00'

    def test_cannot_create_contract_without_hours(self):
        form = ContractForm(data={'department': 'GU'}, user=self.user)
        assert not form.is_valid()

    def test_cannot_create_contract_only_with_start_or_end_date(self):
        expected_error = 'You need to specify both an end date for the contract.'
        form = ContractForm(
            data={
                'department': 'GU',
                'hours': 40,
                'start_date': '01.04.2018',
            },
            user=self.user
        )
        assert not form.is_valid()
        assert 'end_date' in form.errors
        assert form.errors['__all__'][0] == expected_error

        expected_error = 'You need to specify both a start date for the contract.'
        form = ContractForm(
            data={
                'department': 'GU',
                'hours': 40,
                'end_date': '30.04.2018',
            },
            user=self.user
        )
        assert not form.is_valid()
        assert 'start_date' in form.errors
        assert form.errors['__all__'][0] == expected_error

    def test_start_date_must_be_bigger_than_end_date(self):
        expected_error = 'The end date must be bigger than the start date.'
        form = ContractForm(
            data={
                'department': 'GU',
                'hours': 40,
                'start_date': '30.04.2018',
                'end_date': '01.04.2018'
            },
            user=self.user
        )

        assert not form.is_valid()
        assert 'start_date' in form.errors
        assert 'end_date' in form.errors
        assert form.errors['__all__'][0] == expected_error
