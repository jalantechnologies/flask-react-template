import unittest
from typing import Callable

from modules.account.internal.store.account_repository import AccountRepository
from modules.account.rest_api.account_rest_api_server import AccountRestApiServer
from modules.authentication.internals.otp.store.otp_repository import OTPRepository
from modules.notification.internals.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)


class BaseTestAccount(unittest.TestCase):
    def setup_method(self, method: Callable) -> None:
        print(f"Executing:: {method.__name__}")
        AccountRestApiServer.create()

    def teardown_method(self, method: Callable) -> None:
        print(f"Executed:: {method.__name__}")
        AccountRepository.collection().delete_many({})
        OTPRepository.collection().delete_many({})
        AccountNotificationPreferencesRepository.collection().delete_many({})
