from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from plugins.identity.user import (
    RegistrationData,
    RegistrationDataFactory,
    UserAssertion,
    UserData,
)

from server.apps.identity.models import User


@pytest.mark.django_db()
def test_valid_registration(
    client: Client,
    registration_data: 'RegistrationData',
    expected_user_data: 'UserData',
    assert_correct_user: 'UserAssertion',
) -> None:
    """Test that registration works with correct user data."""
    response = client.post(
        reverse('identity:registration'),
        data=registration_data,
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('identity:login')
    assert_correct_user(registration_data['email'], expected_user_data)


@pytest.mark.django_db()
def test_registration_missing_required_field(
    client: Client,
    registration_data_factory: 'RegistrationDataFactory',
) -> None:
    """Test that missing required will fail the registration."""
    post_data = registration_data_factory(email='')
    response = client.post(
        reverse('identity:registration'),
        data=post_data,
    )
    assert response.status_code == HTTPStatus.OK
    assert not User.objects.filter(email=post_data['email'])


@pytest.mark.timeout(5)
@pytest.mark.django_db()
def test_registration_same_email_twice(
    client: Client,
    registration_data: 'RegistrationData',
    expected_user_data: 'UserData',
    assert_correct_user: 'UserAssertion',
    registration_data_factory: 'RegistrationDataFactory',
) -> None:
    """Test that registration works with correct user data."""
    response = client.post(
        reverse('identity:registration'),
        data=registration_data,
    )

    second_user = registration_data_factory(email=registration_data['email'])
    response = client.post(
        reverse('identity:registration'),
        data=second_user,
    )

    assert response.status_code == HTTPStatus.OK
    assert_correct_user(registration_data['email'], expected_user_data)
