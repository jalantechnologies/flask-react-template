"""
App Bootstrap Script

Encapsulates all one-time bootstrapping tasks in a class for extensibility and clarity.
Only runs in development and preview environments.
"""

from modules.account.account_service import AccountService
from modules.account.errors import AccountWithUserNameExistsError
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.config.config_service import ConfigService
from modules.config.errors import MissingKeyError
from modules.logger.logger import Logger


class BootstrapApp:
    def __init__(self) -> None:
        self.enabled = ConfigService[bool].get_value(key="account.enable_bootstrap_tasks", default=False)

    def run(self) -> None:
        if not self.enabled:
            return
        Logger.info(message="Running app bootstrap tasks...")
        self.seed_test_user()
        Logger.info(message="App bootstrap tasks completed.")

    def seed_test_user(self) -> None:
        try:
            create_test_user = ConfigService[bool].get_value(key="account.create_test_user_account")
            if not create_test_user:
                return
            test_user = ConfigService[dict].get_value(key="account.test_user")
            username = test_user.get("username")
            password = test_user.get("password")
            first_name = test_user.get("first_name", "Test")
            last_name = test_user.get("last_name", "User")
            if not isinstance(username, str) or not isinstance(password, str):
                Logger.error(message="Test user 'username' and 'password' must be set in config and be strings.")
                return
            try:
                AccountService.get_account_by_username(username=username)
                return
            except Exception:
                pass
            try:
                params = CreateAccountByUsernameAndPasswordParams(
                    username=username, password=password, first_name=first_name, last_name=last_name
                )
                AccountService.create_account_by_username_and_password(params=params)
                Logger.info(message=f"Test user '{username}' created.")
            except AccountWithUserNameExistsError:
                Logger.info(message=f"Test user '{username}' already exists.")
            except Exception as e:
                Logger.error(message=f"Failed to create test user: {e}")
        except MissingKeyError as e:
            Logger.info(message=f"Skipping test user seeding: {e}")
        except Exception as e:
            Logger.error(message=f"Unexpected error in seed_test_user: {e}")
