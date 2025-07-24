import unittest
from typing import Callable

from modules.account.internal.store.account_repository import AccountRepository
from modules.logger.logger_manager import LoggerManager
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.rest_api.task_rest_api_server import TaskRestApiServer


class BaseTestTask(unittest.TestCase):
    def setup_method(self, method: Callable) -> None:
        print(f"Executing:: {method.__name__}")
        LoggerManager.mount_logger()
        TaskRestApiServer.create()

    def teardown_method(self, method: Callable) -> None:
        print(f"Executed:: {method.__name__}")
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})
