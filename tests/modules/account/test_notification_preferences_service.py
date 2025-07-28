from modules.account.account_service import AccountService
from modules.account.types import (
    CreateAccountByUsernameAndPasswordParams,
    CreateAccountByPhoneNumberParams,
    PhoneNumber,
)
from modules.notification.errors import AccountNotificationPreferencesNotFoundError
from modules.notification.notification_service import NotificationService
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams

from tests.modules.account.base_test_account import BaseTestAccount


class TestNotificationPreferencesService(BaseTestAccount):
    def test_get_notification_preferences_returns_existing_preferences(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        update_preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=False, push_enabled=True, sms_enabled=False
        )
        NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=update_preferences
        )

        preferences = NotificationService.get_account_notification_preferences_by_account_id(account_id=account.id)

        assert preferences.account_id == account.id
        assert preferences.email_enabled is False
        assert preferences.push_enabled is True
        assert preferences.sms_enabled is False

    def test_update_notification_preferences_creates_new_when_none_exist(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        update_preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=False, push_enabled=False, sms_enabled=True
        )

        preferences = NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=update_preferences
        )

        assert preferences.account_id == account.id
        assert preferences.email_enabled is False
        assert preferences.push_enabled is False
        assert preferences.sms_enabled is True

        retrieved_preferences = NotificationService.get_account_notification_preferences_by_account_id(
            account_id=account.id
        )
        assert retrieved_preferences.account_id == account.id
        assert retrieved_preferences.email_enabled is False
        assert retrieved_preferences.push_enabled is False
        assert retrieved_preferences.sms_enabled is True

    def test_create_notification_preferences_with_defaults_for_none_values(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        update_preferences = CreateOrUpdateAccountNotificationPreferencesParams(email_enabled=False)

        preferences = NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=update_preferences
        )

        assert preferences.account_id == account.id
        assert preferences.email_enabled is False
        assert preferences.push_enabled is True
        assert preferences.sms_enabled is True

    def test_update_notification_preferences_updates_existing(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        initial_preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=True, push_enabled=True, sms_enabled=True
        )
        NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=initial_preferences
        )

        update_preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=False, push_enabled=True, sms_enabled=False
        )

        preferences = NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=update_preferences
        )

        assert preferences.account_id == account.id
        assert preferences.email_enabled is False
        assert preferences.push_enabled is True
        assert preferences.sms_enabled is False

        retrieved_preferences = NotificationService.get_account_notification_preferences_by_account_id(
            account_id=account.id
        )
        assert retrieved_preferences.account_id == account.id
        assert retrieved_preferences.email_enabled is False
        assert retrieved_preferences.push_enabled is True
        assert retrieved_preferences.sms_enabled is False

    def test_partial_update_notification_preferences_only_updates_provided_fields(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        initial_preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=True, push_enabled=True, sms_enabled=True
        )
        NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=initial_preferences
        )

        partial_update = CreateOrUpdateAccountNotificationPreferencesParams(email_enabled=False)

        preferences = NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=partial_update
        )

        assert preferences.account_id == account.id
        assert preferences.email_enabled is False
        assert preferences.push_enabled is True
        assert preferences.sms_enabled is True

    def test_partial_update_multiple_fields(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        initial_preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=True, push_enabled=True, sms_enabled=True
        )
        NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=initial_preferences
        )

        partial_update = CreateOrUpdateAccountNotificationPreferencesParams(email_enabled=False, sms_enabled=False)

        preferences = NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=partial_update
        )

        assert preferences.account_id == account.id
        assert preferences.email_enabled is False
        assert preferences.push_enabled is True
        assert preferences.sms_enabled is False

    def test_update_notification_preferences_all_disabled(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        update_preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=False, push_enabled=False, sms_enabled=False
        )

        preferences = NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=update_preferences
        )

        assert preferences.account_id == account.id
        assert preferences.email_enabled is False
        assert preferences.push_enabled is False
        assert preferences.sms_enabled is False

    def test_account_creation_by_username_automatically_creates_notification_preferences(self):
        """Test that creating an account by username automatically creates notification preferences"""
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password="password123", username="testuser@example.com"
            )
        )

        preferences = NotificationService.get_account_notification_preferences_by_account_id(account_id=account.id)

        assert preferences.account_id == account.id
        assert preferences.email_enabled is True
        assert preferences.push_enabled is True
        assert preferences.sms_enabled is True

    def test_account_creation_by_phone_automatically_creates_notification_preferences(self):
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        preferences = NotificationService.get_account_notification_preferences_by_account_id(account_id=account.id)

        assert preferences.account_id == account.id
        assert preferences.email_enabled is True
        assert preferences.push_enabled is True
        assert preferences.sms_enabled is True
