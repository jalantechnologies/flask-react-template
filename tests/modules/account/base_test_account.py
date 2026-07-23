import unittest
from typing import Callable

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.rest_api.account_rest_api_server import AccountRestApiServer
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.internals.otp.store.otp_repository import OTPRepository
from modules.notification.internals.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)


class BaseTestAccount(unittest.TestCase):
    def setup_method(self, method: Callable[..., object]) -> None:
        print(f"Executing:: {method.__name__}")
        AccountRestApiServer.create()
        self.account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="default_username"
            )
        )
        self.access_token = AuthenticationService.create_access_token_by_username_and_password(account=self.account)

    def teardown_method(self, method: Callable[..., object]) -> None:
        print(f"Executed:: {method.__name__}")
        AccountRepository.collection().delete_many({})
        OTPRepository.collection().delete_many({})
        AccountNotificationPreferencesRepository.collection().delete_many({})
