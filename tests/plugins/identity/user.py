import datetime as dt
from typing import Callable, Protocol, TypeAlias, TypedDict, Unpack, final


class UserData(TypedDict, total=False):
    """
    Represent the simplified user data that is required to create a new user.
    It does not include ``password``, because it is very special in django.
    Importing this type is only allowed under ``if TYPE_CHECKING`` in tests.
    """
    email: str
    first_name: str
    last_name: str
    date_of_birth: dt.datetime
    address: str
    job_title: str
    phone: str
    phone_type: int


@final
class RegistrationData(UserData, total=False):
    """
    Represent the registration data that is required to create a new user.
    Importing this type is only allowed under ``if TYPE_CHECKING`` in tests.
    """
    password1: str
    password2: str


@final
class RegistrationDataFactory(Protocol):
	def __call__(
		self,
		**fields: Unpack[RegistrationData],
	) -> RegistrationData:
		"""User data factory protocol."""


UserAssertion: TypeAlias = Callable[[str, UserData], None]
