import json

from web_app import app

from modules.account.account_service import AccountService
from modules.account.internal.account_writer import AccountWriter
from modules.account.types import (
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams
from tests.conftest import TEST_ACTOR
from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestNotificationPreferencesService(BaseTestAccount):
    def _create_account_and_get_token(self, username: str) -> tuple[str, str]:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username=username
            ),
            actor=TEST_ACTOR,
        )
        token = AuthenticationService.create_access_token_by_username_and_password(account=account).token
        return account.id, token

    def _create_phone_account_and_get_token(self, phone_number: dict[str, str]) -> tuple[str, str]:
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number)), actor=TEST_ACTOR
        )
        AccountService.create_or_update_account_notification_preferences(
            account_id=account.id,
            actor=TEST_ACTOR,
            preferences=CreateOrUpdateAccountNotificationPreferencesParams(
                email_enabled=True, push_enabled=True, sms_enabled=True
            ),
        )
        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id, actor=TEST_ACTOR
        )
        with app.test_client() as client:
            response = client.post(
                ACCESS_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"phone_number": phone_number, "otp_code": otp.otp_code}),
            )
            assert response.json is not None
            return account.id, response.json["token"]

    def _patch_preferences(self, account_id: str, token: str, preferences: dict[str, bool]) -> None:
        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(preferences),
            )
            assert response.status_code == 200

    def _get_preferences(self, account_id: str, token: str) -> dict[str, object]:
        with app.test_client() as client:
            response = client.get(
                f"{ACCOUNT_URL}/{account_id}?include_notification_preferences=true",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200
            assert response.json is not None
            preferences = response.json["notification_preferences"]
            assert isinstance(preferences, dict)
            return preferences

    def test_get_notification_preferences_returns_existing_preferences(self) -> None:
        account_id, token = self._create_account_and_get_token("username")
        self._patch_preferences(account_id, token, {"email_enabled": False, "push_enabled": True, "sms_enabled": False})

        preferences = self._get_preferences(account_id, token)

        assert preferences["account_id"] == account_id
        assert preferences["email_enabled"] is False
        assert preferences["push_enabled"] is True
        assert preferences["sms_enabled"] is False

    def test_update_notification_preferences_creates_new_when_none_exist(self) -> None:
        account_id, token = self._create_account_and_get_token("username")

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps({"email_enabled": False, "push_enabled": False, "sms_enabled": True}),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json["account_id"] == account_id
        assert response.json["email_enabled"] is False
        assert response.json["push_enabled"] is False
        assert response.json["sms_enabled"] is True

        preferences = self._get_preferences(account_id, token)
        assert preferences["account_id"] == account_id
        assert preferences["email_enabled"] is False
        assert preferences["push_enabled"] is False
        assert preferences["sms_enabled"] is True

    def test_create_notification_preferences_with_defaults_for_none_values(self) -> None:
        account_id, token = self._create_account_and_get_token("username")

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps({"email_enabled": False}),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json["account_id"] == account_id
        assert response.json["email_enabled"] is False
        assert response.json["push_enabled"] is True
        assert response.json["sms_enabled"] is True

    def test_update_notification_preferences_updates_existing(self) -> None:
        account_id, token = self._create_account_and_get_token("username")
        self._patch_preferences(account_id, token, {"email_enabled": True, "push_enabled": True, "sms_enabled": True})

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps({"email_enabled": False, "push_enabled": True, "sms_enabled": False}),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json["account_id"] == account_id
        assert response.json["email_enabled"] is False
        assert response.json["push_enabled"] is True
        assert response.json["sms_enabled"] is False

        preferences = self._get_preferences(account_id, token)
        assert preferences["account_id"] == account_id
        assert preferences["email_enabled"] is False
        assert preferences["push_enabled"] is True
        assert preferences["sms_enabled"] is False

    def test_partial_update_notification_preferences_only_updates_provided_fields(self) -> None:
        account_id, token = self._create_account_and_get_token("username")
        self._patch_preferences(account_id, token, {"email_enabled": True, "push_enabled": True, "sms_enabled": True})

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps({"email_enabled": False}),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json["account_id"] == account_id
        assert response.json["email_enabled"] is False
        assert response.json["push_enabled"] is True
        assert response.json["sms_enabled"] is True

    def test_partial_update_multiple_fields(self) -> None:
        account_id, token = self._create_account_and_get_token("username")
        self._patch_preferences(account_id, token, {"email_enabled": True, "push_enabled": True, "sms_enabled": True})

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps({"email_enabled": False, "sms_enabled": False}),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json["account_id"] == account_id
        assert response.json["email_enabled"] is False
        assert response.json["push_enabled"] is True
        assert response.json["sms_enabled"] is False

    def test_update_notification_preferences_all_disabled(self) -> None:
        account_id, token = self._create_account_and_get_token("username")

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps({"email_enabled": False, "push_enabled": False, "sms_enabled": False}),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json["account_id"] == account_id
        assert response.json["email_enabled"] is False
        assert response.json["push_enabled"] is False
        assert response.json["sms_enabled"] is False

    def test_account_creation_by_username_automatically_creates_notification_preferences(self) -> None:
        with app.test_client() as client:
            create_response = client.post(
                ACCOUNT_URL,
                headers=HEADERS,
                data=json.dumps(
                    {
                        "first_name": "Test",
                        "last_name": "User",
                        "password": "password123",
                        "username": "testuser@example.com",
                    }
                ),
            )
            assert create_response.status_code == 201
            assert create_response.json is not None
            account_id = create_response.json["id"]

            token_response = client.post(
                ACCESS_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"username": "testuser@example.com", "password": "password123"}),
            )
            assert token_response.json is not None
            token = token_response.json["token"]

        preferences = self._get_preferences(account_id, token)
        assert preferences["account_id"] == account_id
        assert preferences["email_enabled"] is True
        assert preferences["push_enabled"] is True
        assert preferences["sms_enabled"] is True

    def test_account_creation_by_phone_automatically_creates_notification_preferences(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account_id, token = self._create_phone_account_and_get_token(phone_number)

        preferences = self._get_preferences(account_id, token)
        assert preferences["account_id"] == account_id
        assert preferences["email_enabled"] is True
        assert preferences["push_enabled"] is True
        assert preferences["sms_enabled"] is True
