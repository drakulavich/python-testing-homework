from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from plugins.identity.user import RegistrationData

from server.apps.pictures.models import FavouritePicture


def signin_user(client: Client, registration_data: 'RegistrationData') -> None:
    """Register and sign in user."""
    client.post(
        reverse('identity:registration'),
        data=registration_data,
    )

    response = client.post(
        reverse('identity:login'),
        data={
            'username': registration_data['email'],
            'password': registration_data['password1'],
        },
    )

    assert response.status_code == HTTPStatus.FOUND


def test_anonymous_user_get_dashboard(
    client: Client,
) -> None:
    """Test anonymous User gets pictures dashboard."""
    response = client.get(reverse('pictures:dashboard'))

    assert response.status_code == HTTPStatus.FOUND
    assert reverse('identity:login') in response.get('Location')


@pytest.mark.django_db()
def test_signed_user_get_dashboard(
    client: Client,
    registration_data: 'RegistrationData',
) -> None:
    """Test signed User gets pictures dashboard."""
    signin_user(client, registration_data)

    response = client.get(reverse('pictures:dashboard'))

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_signed_user_favorite_picture(
    client: Client,
    registration_data: 'RegistrationData',
) -> None:
    """Test signed User favorites picture."""
    signin_user(client, registration_data)

    response = client.post(
        reverse('pictures:dashboard'),
        data={
            'foreign_id': 1,
            'url': 'https://via.placeholder.com/600/92c952',
        },
    )

    assert response.status_code == HTTPStatus.FOUND
    assert reverse('pictures:dashboard') in response.get('Location')
    assert FavouritePicture.objects.count() == 1
