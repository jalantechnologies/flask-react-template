import os
from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.config.errors import MissingKeyError


class BootstrapApp:
    def __init__(self) -> None:
        self.should_bootstrap = ConfigService[bool].get_value(key="BOOTSTRAP_APP")

    def run(self) -> None:
        if not self.should_bootstrap:
            Logger.info(message="App bootstrap is disabled by config flag.")
            return
        Logger.info(message="Running app bootstrap tasks...")
        self.seed_test_user()

    def seed_test_user(self) -> None:
        try:
            create_test_user = ConfigService[bool].get_value(key="accounts.create_test_user_account")
            if not create_test_user:
                return
            try:
                username = ConfigService[str].get_value(key="accounts.test_user.username")
                password = ConfigService[str].get_value(key="accounts.test_user.password")
                first_name = ConfigService[str].get_value(key="accounts.test_user.first_name")
                last_name = ConfigService[str].get_value(key="accounts.test_user.last_name")
            except MissingKeyError as e:
                Logger.info(message=f"Skipping test user seeding: {e}")
                return
            params = CreateAccountByUsernameAndPasswordParams(
                username=username, password=password, first_name=first_name, last_name=last_name
            )
            try:
                AccountService.create_account_by_username_and_password(params=params)
                Logger.info(message=f"Test user '{username}' created.")
            except Exception as e:
                Logger.error(message=f"Failed to create test user: {e}")
        except MissingKeyError as e:
            Logger.info(message=f"Skipping test user seeding: {e}")
        except Exception as e:
            Logger.error(message=f"Unexpected error in seed_test_user: {e}")


if __name__ == "__main__":
    BootstrapApp().run()
