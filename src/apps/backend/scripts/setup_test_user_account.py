from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.config.config_service import ConfigService
from modules.account.errors import AccountWithUserNameExistsError
from modules.logger.logger import Logger

def setup_test_user_account() -> None:
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

if __name__ == "__main__":
    setup_test_user_account() 