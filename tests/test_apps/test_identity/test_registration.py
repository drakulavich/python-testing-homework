import pytest
from typing import Unpack

from http import HTTPStatus

from mimesis.locales import Locale
from mimesis.schema import Field, Schema

from django.test import Client
from django.urls import reverse


from tests.plugins.identity.user import (
    RegistrationData,
    RegistrationDataFactory,
    UserAssertion,
    UserData,
)


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
            'phone_type': mf('choice', items=[1, 2, 3]),
        })
		return {
            **schema.create(iterations=1)[0], # type: ignore[misc]
            **{'password1': password, 'password2': password},
            **fields,
        }
	return factory


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
