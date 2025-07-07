import unittest
from typing import Callable

from modules.account.internal.store.account_repository import AccountRepository
from modules.authentication.internals.otp.store.otp_repository import OTPRepository
from modules.authentication.rest_api.authentication_rest_api_server import AuthenticationRestApiServer


class BaseTestAccessToken(unittest.TestCase):
    def setup_method(self, method: Callable) -> None:
        print(f"Executing:: {method.__name__}")
        AuthenticationRestApiServer.create()

    def teardown_method(self, method: Callable) -> None:
        print(f"Executed:: {method.__name__}")
        AccountRepository.collection().delete_many({})
        OTPRepository.collection().delete_many({})
