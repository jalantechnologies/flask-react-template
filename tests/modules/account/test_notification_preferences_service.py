from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.notification.errors import NotificationPreferencesNotFoundError
from modules.notification.types import NotificationPreferencesParams

from tests.modules.account.base_test_account import BaseTestAccount


class TestNotificationPreferencesService(BaseTestAccount):
    def test_get_notification_preferences_throws_error_when_none_exist(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with self.assertRaises(NotificationPreferencesNotFoundError):
            AccountService.get_notification_preferences(account_id=account.id)

    def test_get_notification_preferences_returns_existing_preferences(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        update_preferences = NotificationPreferencesParams(email_enabled=False, push_enabled=True, sms_enabled=False)
        AccountService.update_notification_preferences(account_id=account.id, preferences=update_preferences)

        preferences = AccountService.get_notification_preferences(account_id=account.id)

        assert preferences.email_enabled is False
        assert preferences.push_enabled is True
        assert preferences.sms_enabled is False

    def test_update_notification_preferences_creates_new_when_none_exist(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        update_preferences = NotificationPreferencesParams(email_enabled=False, push_enabled=False, sms_enabled=True)

        preferences = AccountService.update_notification_preferences(
            account_id=account.id, preferences=update_preferences
        )

        assert preferences.email_enabled is False
        assert preferences.push_enabled is False
        assert preferences.sms_enabled is True

        retrieved_preferences = AccountService.get_notification_preferences(account_id=account.id)
        assert retrieved_preferences.email_enabled is False
        assert retrieved_preferences.push_enabled is False
        assert retrieved_preferences.sms_enabled is True

    def test_update_notification_preferences_updates_existing(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        initial_preferences = NotificationPreferencesParams(email_enabled=True, push_enabled=True, sms_enabled=True)
        AccountService.update_notification_preferences(account_id=account.id, preferences=initial_preferences)

        update_preferences = NotificationPreferencesParams(email_enabled=False, push_enabled=True, sms_enabled=False)

        preferences = AccountService.update_notification_preferences(
            account_id=account.id, preferences=update_preferences
        )

        assert preferences.email_enabled is False
        assert preferences.push_enabled is True
        assert preferences.sms_enabled is False

        retrieved_preferences = AccountService.get_notification_preferences(account_id=account.id)
        assert retrieved_preferences.email_enabled is False
        assert retrieved_preferences.push_enabled is True
        assert retrieved_preferences.sms_enabled is False

    def test_update_notification_preferences_all_disabled(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        update_preferences = NotificationPreferencesParams(email_enabled=False, push_enabled=False, sms_enabled=False)

        preferences = AccountService.update_notification_preferences(
            account_id=account.id, preferences=update_preferences
        )

        assert preferences.email_enabled is False
        assert preferences.push_enabled is False
        assert preferences.sms_enabled is False
