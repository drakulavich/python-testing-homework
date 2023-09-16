from http import HTTPStatus

import pytest
from django.test import Client


@pytest.mark.django_db()
def test_user_can_register(client: Client) -> None:
    """This test ensures that user can register."""
    user = {
        'email': 'ayak@dev.null',
        'job_title': 'developer',
        'first_name': 'Ayak',
        'last_name': 'Sibak',
        'address': 'Somewhere',
        'date_of_birth': '2000-01-01',
        'phone': '+1234567890',
        'password1': 'new-admin-password',
        'password2': 'new-admin-password',
    }
    response = client.post(
        '/identity/registration',
        data=user,
    )

    assert not response.content.decode()
    assert response.status_code == HTTPStatus.FOUND

    new_user = {
        'username': 'ayak@dev.null',
        'password': 'new-admin-password',
    }
    response = client.post(
        '/identity/login',
        data=new_user,
    )

    assert not response.content.decode()
    assert response.status_code == HTTPStatus.FOUND
