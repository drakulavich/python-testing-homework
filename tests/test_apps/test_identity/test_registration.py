from http import HTTPStatus
import random
from typing import Unpack

import pytest
from django.test import Client
from django.urls import reverse
from mimesis.locales import Locale
from mimesis.schema import Field, Schema

from plugins.identity.user import (
    RegistrationData,
    RegistrationDataFactory,
    UserAssertion,
    UserData,
)

from server.apps.identity.models import User


@pytest.fixture(scope='session')
def assert_correct_user() -> UserAssertion:
	def factory(email: str, expected: UserData) -> None:
		user = User.objects.get(email=email)
		# Special fields:
		assert user.id
		assert user.is_active
		assert not user.is_superuser
		assert not user.is_staff
		# All other fields:
		for field_name, data_value in expected.items():
			assert getattr(user, field_name) == data_value
	return factory

@pytest.fixture()
def registration_data_factory(faker_seed: int) -> RegistrationDataFactory:
	"""Returns factory for fake random data for regitration."""
	def factory(**fields: Unpack[RegistrationData]) -> RegistrationData:
		mf = Field(locale=Locale.RU, seed=faker_seed)
		password = mf('password') # by default passwords are equal
		schema = Schema(schema=lambda: {
            'email': mf('person.email'),
            'first_name': mf('person.first_name'),
            'last_name': mf('person.last_name'),
            'date_of_birth': mf('datetime.date'),
            'address': mf('address.city'),
            'job_title': mf('person.occupation'),
            'phone': mf('person.telephone'),
        }, iterations=1)
		return {
			**schema.create()[0], # type: ignore[misc]
			**{'password1': password, 'password2': password},
			**fields,
		}
	return factory

@pytest.fixture(scope="session")
def faker_seed():
    return random.Random().getrandbits(32)

@pytest.fixture()
def registration_data(
    registration_data_factory: RegistrationDataFactory,
) -> RegistrationData:
	"""Returns fake random data for regitration."""
	return registration_data_factory()

@pytest.fixture()
def user_data(registration_data: 'RegistrationData') -> 'UserData':
	"""
	We need to simplify registration data to drop passwords.
	Basically, it is the same as ``registration_data``, but without passwords.
	"""
	return { # type: ignore[return-value]
		key_name: value_part
		for key_name, value_part in registration_data.items()
		if not key_name.startswith('password')
	}

@pytest.fixture()
def expected_user_data(user_data: RegistrationData):
    return user_data

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
