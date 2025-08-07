import json

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.authentication.types import AccessTokenErrorCode
from modules.notification.notification_service import NotificationService
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams
from server import app

from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
HEADERS = {"Content-Type": "application/json"}


class TestNotificationPreferencesApi(BaseTestAccount):
    def test_get_account_with_notification_preferences_included(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        default_preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=True, push_enabled=True, sms_enabled=True
        )
        NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=default_preferences
        )

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            response = client.get(
                f"{ACCOUNT_URL}/{account.id}?include_notification_preferences=true",
                headers={"Authorization": f"Bearer {access_token_response.json.get('token')}"},
            )

            assert response.status_code == 200
            assert response.json
            assert "notification_preferences" in response.json
            assert response.json["notification_preferences"]["email_enabled"] is True
            assert response.json["notification_preferences"]["push_enabled"] is True
            assert response.json["notification_preferences"]["sms_enabled"] is True
            assert "account_id" in response.json["notification_preferences"]
            assert response.json["notification_preferences"]["account_id"] == account.id

    def test_get_account_without_notification_preferences_parameter(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            response = client.get(
                f"{ACCOUNT_URL}/{account.id}",
                headers={"Authorization": f"Bearer {access_token_response.json.get('token')}"},
            )

            assert response.status_code == 200
            assert response.json
            assert "notification_preferences" not in response.json

    def test_get_account_with_notification_preferences_false(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            response = client.get(
                f"{ACCOUNT_URL}/{account.id}?include_notification_preferences=false",
                headers={"Authorization": f"Bearer {access_token_response.json.get('token')}"},
            )

            assert response.status_code == 200
            assert response.json
            assert "notification_preferences" not in response.json

    def test_update_notification_preferences_success(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

            response = client.patch(
                f"{ACCOUNT_URL}/{account.id}/notification-preferences",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token_response.json.get('token')}",
                },
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json["email_enabled"] is False
            assert response.json["push_enabled"] is True
            assert response.json["sms_enabled"] is False
            assert "account_id" in response.json
            assert response.json["account_id"] == account.id

    def test_update_notification_preferences_partial_update_single_field(self) -> None:
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

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            preferences_data = {"email_enabled": False}

            response = client.patch(
                f"{ACCOUNT_URL}/{account.id}/notification-preferences",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token_response.json.get('token')}",
                },
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json["email_enabled"] is False
            assert response.json["push_enabled"] is True
            assert response.json["sms_enabled"] is True
            assert "account_id" in response.json
            assert response.json["account_id"] == account.id

    def test_update_notification_preferences_partial_update_multiple_fields(self) -> None:
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

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            preferences_data = {"email_enabled": False, "sms_enabled": False}

            response = client.patch(
                f"{ACCOUNT_URL}/{account.id}/notification-preferences",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token_response.json.get('token')}",
                },
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json["email_enabled"] is False
            assert response.json["push_enabled"] is True
            assert response.json["sms_enabled"] is False
            assert "account_id" in response.json
            assert response.json["account_id"] == account.id

    def test_update_notification_preferences_empty_body_returns_error(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            response = client.patch(
                f"{ACCOUNT_URL}/{account.id}/notification-preferences",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token_response.json.get('token')}",
                },
                data=json.dumps({}),
            )

            assert response.status_code == 400
            assert response.json
            assert "At least one preference field" in response.json["message"]

    def test_update_notification_preferences_no_valid_fields_returns_error(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            preferences_data = {"invalid_field": True, "another_invalid": False}

            response = client.patch(
                f"{ACCOUNT_URL}/{account.id}/notification-preferences",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token_response.json.get('token')}",
                },
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 400
            assert response.json
            assert "At least one preference field" in response.json["message"]

    def test_update_notification_preferences_invalid_boolean_value(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            preferences_data = {"email_enabled": "not_a_boolean"}

            response = client.patch(
                f"{ACCOUNT_URL}/{account.id}/notification-preferences",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token_response.json.get('token')}",
                },
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 400
            assert response.json
            assert "email_enabled must be a boolean" in response.json["message"]

    def test_update_notification_preferences_no_auth(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

            response = client.patch(
                f"{ACCOUNT_URL}/{account.id}/notification-preferences",
                headers=HEADERS,
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json["email_enabled"] is False
            assert response.json["push_enabled"] is True
            assert response.json["sms_enabled"] is False
            assert "account_id" in response.json
            assert response.json["account_id"] == account.id

    def test_update_notification_preferences_invalid_token(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

            response = client.patch(
                f"{ACCOUNT_URL}/{account.id}/notification-preferences",
                headers={"Content-Type": "application/json", "Authorization": "Bearer invalid_token"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json["email_enabled"] is False
            assert response.json["push_enabled"] is True
            assert response.json["sms_enabled"] is False
            assert "account_id" in response.json
            assert response.json["account_id"] == account.id

    def test_update_notification_preferences_different_account(self) -> None:
        account1 = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name1", last_name="last_name1", password="password1", username="username1"
            )
        )

        account2 = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name2", last_name="last_name2", password="password2", username="username2"
            )
        )

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account1.username, "password": "password1"}),
            )

            preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

            response = client.patch(
                f"{ACCOUNT_URL}/{account2.id}/notification-preferences",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token_response.json.get('token')}",
                },
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json["email_enabled"] is False
            assert response.json["push_enabled"] is True
            assert response.json["sms_enabled"] is False
            assert "account_id" in response.json
            assert response.json["account_id"] == account2.id
