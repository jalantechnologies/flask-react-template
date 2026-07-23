import json

from web_app import app

from modules.account.account_service import AccountService
from modules.account.types import AccountErrorCode, CreateAccountByUsernameAndPasswordParams
from modules.authentication.types import AccessTokenErrorCode
from modules.notification.notification_service import NotificationService
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams
from tests.conftest import TEST_ACTOR
from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
HEADERS = {"Content-Type": "application/json"}


class TestNotificationPreferencesApi(BaseTestAccount):
    def test_given_existing_preferences_when_getting_account_with_preferences_requested_then_returns_preferences(
        self,
    ) -> None:
        preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=True, push_enabled=True, sms_enabled=True
        )
        NotificationService.create_or_update_account_notification_preferences(
            account_id=self.account.id, actor=TEST_ACTOR, preferences=preferences
        )

        with app.test_client() as client:
            response = client.get(
                f"{ACCOUNT_URL}/{self.account.id}?include_notification_preferences=true",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
            )

            assert response.status_code == 200
            assert response.json
            assert "notification_preferences" in response.json
            assert response.json["notification_preferences"]["email_enabled"] is True
            assert response.json["notification_preferences"]["push_enabled"] is True
            assert response.json["notification_preferences"]["sms_enabled"] is True
            assert response.json["notification_preferences"]["account_id"] == self.account.id

    def test_given_account_when_getting_account_without_preferences_parameter_then_omits_preferences(self) -> None:
        with app.test_client() as client:
            response = client.get(
                f"{ACCOUNT_URL}/{self.account.id}",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
            )

            assert response.status_code == 200
            assert response.json
            assert "notification_preferences" not in response.json

    def test_given_account_when_getting_account_with_preferences_disabled_then_omits_preferences(self) -> None:
        with app.test_client() as client:
            response = client.get(
                f"{ACCOUNT_URL}/{self.account.id}?include_notification_preferences=false",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
            )

            assert response.status_code == 200
            assert response.json
            assert "notification_preferences" not in response.json

    def test_given_authenticated_account_when_updating_all_preferences_then_returns_updated_preferences(self) -> None:
        preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json["email_enabled"] is False
            assert response.json["push_enabled"] is True
            assert response.json["sms_enabled"] is False
            assert response.json["account_id"] == self.account.id

    def test_given_existing_preferences_when_updating_a_single_field_then_updates_only_that_field(self) -> None:
        preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=True, push_enabled=True, sms_enabled=True
        )
        NotificationService.create_or_update_account_notification_preferences(
            account_id=self.account.id, actor=TEST_ACTOR, preferences=preferences
        )
        preferences_data = {"email_enabled": False}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json["email_enabled"] is False
            assert response.json["push_enabled"] is True
            assert response.json["sms_enabled"] is True
            assert response.json["account_id"] == self.account.id

    def test_given_existing_preferences_when_updating_multiple_fields_then_updates_only_those_fields(self) -> None:
        preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=True, push_enabled=True, sms_enabled=True
        )
        NotificationService.create_or_update_account_notification_preferences(
            account_id=self.account.id, actor=TEST_ACTOR, preferences=preferences
        )
        preferences_data = {"email_enabled": False, "sms_enabled": False}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json["email_enabled"] is False
            assert response.json["push_enabled"] is True
            assert response.json["sms_enabled"] is False
            assert response.json["account_id"] == self.account.id

    def test_given_empty_body_when_updating_preferences_then_returns_bad_request(self) -> None:
        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps({}),
            )

            assert response.status_code == 400
            assert response.json
            assert "At least one preference field" in response.json["message"]

    def test_given_no_recognized_fields_when_updating_preferences_then_returns_bad_request(self) -> None:
        preferences_data = {"another_unrecognized_field": False, "unrecognized_field": True}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 400
            assert response.json
            assert "At least one preference field" in response.json["message"]

    def test_given_non_boolean_field_when_updating_preferences_then_returns_bad_request(self) -> None:
        preferences_data = {"email_enabled": "not_a_boolean"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 400
            assert response.json
            assert "email_enabled must be a boolean" in response.json["message"]

    def test_given_null_request_body_when_updating_preferences_then_returns_bad_request(self) -> None:
        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(None),
            )

            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == AccountErrorCode.BAD_REQUEST

    def test_given_numeric_request_body_when_updating_preferences_then_returns_bad_request(self) -> None:
        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(123),
            )

            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == AccountErrorCode.BAD_REQUEST

    def test_given_string_request_body_when_updating_preferences_then_returns_bad_request(self) -> None:
        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps("email_enabled"),
            )

            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == AccountErrorCode.BAD_REQUEST

    def test_given_no_authorization_header_when_updating_preferences_then_returns_unauthorized(self) -> None:
        preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers=HEADERS,
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_given_invalid_access_token_when_updating_preferences_then_returns_unauthorized(self) -> None:
        preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": "Bearer invalid_token"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_INVALID

    def test_given_authorization_header_without_a_token_when_updating_preferences_then_returns_unauthorized(
        self,
    ) -> None:
        preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": "Bearer"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.INVALID_AUTHORIZATION_HEADER

    def test_given_authorization_header_with_extra_whitespace_when_updating_preferences_then_returns_unauthorized(
        self,
    ) -> None:
        preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer  {self.access_token.token}"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.INVALID_AUTHORIZATION_HEADER

    def test_given_authenticated_account_when_updating_another_users_preferences_then_returns_unauthorized(
        self,
    ) -> None:
        other_account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="other_first_name", last_name="other_last_name", password="password", username="other_user"
            ),
            actor=TEST_ACTOR,
        )
        preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{other_account.id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.UNAUTHORIZED_ACCESS

    def test_given_authenticated_account_when_updating_a_nonexistent_account_then_returns_unauthorized(self) -> None:
        nonexistent_account_id = "661e42ec98423703a299a899"
        preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{nonexistent_account_id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.UNAUTHORIZED_ACCESS

    def test_given_authenticated_account_when_updating_a_malformed_account_id_then_returns_unauthorized(self) -> None:
        malformed_account_id = "invalid_object_id"
        preferences_data = {"email_enabled": False, "push_enabled": True, "sms_enabled": False}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{malformed_account_id}/notification-preferences",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(preferences_data),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.UNAUTHORIZED_ACCESS
