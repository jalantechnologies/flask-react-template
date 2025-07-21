import unittest
from typing import Callable

from modules.logger.logger_manager import LoggerManager
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository
from modules.notification.rest_api.notification_rest_api_server import NotificationRestApiServer


class BaseTestNotification(unittest.TestCase):
    def setup_method(self, method: Callable) -> None:
        print(f"Executing:: {method.__name__}")
        LoggerManager.mount_logger()
        NotificationRestApiServer.create()

    def teardown_method(self, method: Callable) -> None:
        print(f"Executed:: {method.__name__}")
        DeviceTokenRepository.collection().delete_many({})
