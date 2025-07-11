#!/usr/bin/env python3
"""
App Bootstrap Script

Encapsulates all one-time bootstrapping tasks in a class for extensibility and clarity.
Only runs in development and preview environments.
"""

from modules.logger.logger import Logger
from modules.config.config_service import ConfigService
from modules.config.errors import MissingKeyError
import os

class BootstrapApp:
    def __init__(self) -> None:
        self.env = ConfigService[str].get_value(key="APP_ENV", default=os.environ.get("APP_ENV", "development"))

    def run(self) -> None:
        if self.env not in ("development", "preview"):
            Logger.info(message=f"Bootstrap tasks skipped for environment: {self.env}")
            return
        Logger.info(message="Running app bootstrap tasks...")
        self.seed_test_user()
        # Add more bootstrapping tasks here as methods
        Logger.info(message="App bootstrap tasks completed.")

    def seed_test_user(self) -> None:
        try:
            from modules.account.account_service import AccountService
            from modules.account.types import CreateAccountByUsernameAndPasswordParams
            from modules.account.errors import AccountWithUserNameExistsError

            # Check if test user creation is enabled
            create_test_user = ConfigService[bool].get_value(key="account.create_test_user_account")
            if not create_test_user:
                return

            # Get test user credentials from config
            test_user = ConfigService[dict].get_value(key="account.test_user")
            username = test_user.get("username")
            password = test_user.get("password")
            first_name = test_user.get("first_name", "Test")
            last_name = test_user.get("last_name", "User")

            # Ensure username and password are present
            if not isinstance(username, str) or not isinstance(password, str):
                Logger.error(message="Test user 'username' and 'password' must be set in config and be strings.")
                return

            # Check if user already exists
            try:
                AccountService.get_account_by_username(username=username)
                return  # User already exists
            except Exception:
                pass  # User does not exist, proceed

            # Create the test user
            try:
                params = CreateAccountByUsernameAndPasswordParams(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
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

if __name__ == "__main__":
    BootstrapApp().run() 