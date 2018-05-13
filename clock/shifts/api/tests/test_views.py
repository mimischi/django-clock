from collections import OrderedDict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from clock.shifts.factories import UserFactory


@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def user():
    return UserFactory()


@pytest.mark.django_db
def test_shift_overlap_api_start_after_finish(client):
    """Fail when the finished date is smaller than the started."""
    url = reverse(
        'api:overlap-list',
        kwargs={
            'started': '2018-05-02',
            'finished': '2018-05-01',
            'contract': 1,
            'reoccuring': 'DAILY',
            'pk': 0
        }
    )

    response = client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    ['reoccurence', 'status_code'], [
        ('ONCE', status.HTTP_400_BAD_REQUEST), ('DAILY', status.HTTP_200_OK),
        ('WEEKLY', status.HTTP_200_OK), ('MONTHLY', status.HTTP_200_OK)
    ]
)
def test_shift_overlap_api_reoccurence_string(
    client, reoccurence, status_code
):
    """Check the response depending on the reoccurence string."""
    url = reverse(
        'api:overlap-list',
        kwargs={
            'started': '2018-05-01',
            'finished': '2018-05-02',
            'contract': 1,
            'reoccuring': reoccurence,
            'pk': 0
        }
    )

    response = client.get(url)
    assert response.status_code == status_code


@pytest.mark.django_db
def test_shift_overlap_api_generate_new_shifts(client):
    """Test we can create new shifts, when not overlapping with anything."""
    url = reverse(
        'api:overlap-list',
        kwargs={
            'started': '2018-05-01 05:00',
            'finished': '2018-05-02 08:00',
            'contract': 1,
            'reoccuring': 'DAILY',
            'pk': 0
        }
    )

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    shifts = [
        {
            'started': '2018-05-01T05:00:00+02:00',
            'finished': '2018-05-01T08:00:00+02:00',
            'employee': 6,
            'contract': None
        }, {
            'started': '2018-05-02T05:00:00+02:00',
            'finished': '2018-05-02T08:00:00+02:00',
            'employee': 6,
            'contract': None
        }
    ]
    shifts = [OrderedDict(shift) for shift in shifts]

    without_overlaps = response.data['without_overlap']
    with_overlaps = response.data['with_overlap']
    assert with_overlaps == []
    assert without_overlaps == shifts
