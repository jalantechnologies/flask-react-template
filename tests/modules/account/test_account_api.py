import json
from datetime import datetime, timedelta
from unittest import mock

import jwt
from server import app

from modules.account.account_service import AccountService
from modules.account.types import (
    AccountErrorCode,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.authentication.types import AccessTokenErrorCode, OTPErrorCode
from modules.config.config_service import ConfigService
from modules.notification.sms_service import SMSService
from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
HEADERS = {"Content-Type": "application/json"}


class TestAccountApi(BaseTestAccount):
    def test_create_account_by_username_and_password(self) -> None:
        payload = json.dumps(
            {"first_name": "first_name", "last_name": "last_name", "password": "password", "username": "username"}
        )

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            assert response.status_code == 201
            assert response.json, f"No response from API with status code:: {response.status}"
            assert response.json.get("username") == "username"

    def test_create_account_with_existing_user(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )
        with app.test_client() as client:
            response = client.post(
                ACCOUNT_URL,
                headers=HEADERS,
                data=json.dumps(
                    {
                        "first_name": "first_name",
                        "last_name": "last_name",
                        "password": "password",
                        "username": account.username,
                    }
                ),
            )
        assert response.status_code == 409
        assert response.json
        assert response.json.get("code") == AccountErrorCode.USERNAME_ALREADY_EXISTS

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_create_account_by_phone_number_and_send_otp(self, mock_send_sms) -> None:
        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}})

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "9999999999"})
            self.assertIn("id", response.json)
            self.assertTrue(mock_send_sms.called)
            self.assertEqual(
                mock_send_sms.call_args.kwargs["params"].recipient_phone,
                PhoneNumber(country_code="+91", phone_number="9999999999"),
            )
            self.assertIn(
                "is your One Time Password (OTP) for verification.",
                mock_send_sms.call_args.kwargs["params"].message_body,
            )

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_get_account_with_existing_phone_number_and_send_otp(self, mock_send_sms) -> None:
        AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(
                phone_number=PhoneNumber(**{"country_code": "+91", "phone_number": "9999999999"})
            )
        )
        with app.test_client() as client:
            response = client.post(
                ACCOUNT_URL,
                headers=HEADERS,
                data=json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}}),
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "9999999999"})
        self.assertIn("id", response.json)
        self.assertTrue(mock_send_sms.called)
        self.assertEqual(
            mock_send_sms.call_args.kwargs["params"].recipient_phone,
            PhoneNumber(country_code="+91", phone_number="9999999999"),
        )
        self.assertIn(
            "is your One Time Password (OTP) for verification.", mock_send_sms.call_args.kwargs["params"].message_body
        )

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_get_or_create_account_with_invalid_phone_number(self, mock_send_sms) -> None:
        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "999999999"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 400)
            self.assertTrue(response.json)
            self.assertEqual(response.json.get("code"), OTPErrorCode.REQUEST_FAILED)
            self.assertEqual(response.json.get("message"), "Please provide a valid phone number.")
            self.assertFalse(mock_send_sms.called)

    def test_get_account_by_username_and_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            access_token = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )
            response = client.get(
                f"http://127.0.0.1:8080/api/accounts/{account.id}",
                headers={"Authorization": f"Bearer {access_token.json.get('token')}"},
            )
            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == account.id
            assert response.json.get("username") == account.username
            assert response.json.get("first_name") == account.first_name
            assert response.json.get("last_name") == account.last_name

    def test_get_account_by_username_and_password_with_invalid_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )
            response = client.get(
                f"http://127.0.0.1:8080/api/accounts/{account.id}", headers={"Authorization": f"Bearer invalid_token"}
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_INVALID

    def test_get_account_with_expired_access_token(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        # Create an expired token by setting the expiry to a date in the past using same method as in the
        # access token service
        jwt_signing_key = ConfigService[str].get_value(key="accounts.token_signing_key")
        jwt_expiry = timedelta(days=ConfigService[int].get_value(key="accounts.token_expiry_days") - 1)
        payload = {"account_id": account.id, "exp": (datetime.now() - jwt_expiry).timestamp()}
        expired_token = jwt.encode(payload, jwt_signing_key, algorithm="HS256")

        with app.test_client() as client:
            response = client.get(
                f"http://127.0.0.1:8080/api/accounts/{account.id}", headers={"Authorization": f"Bearer {expired_token}"}
            )

            assert response.status_code == 401
            assert "Access token has expired. Please login again." in response.json.get("message", "")
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_EXPIRED

    def test_update_account_profile_first_name_only(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="old_first_name", last_name="old_last_name", password="password", username="username"
            )
        )

        update_params = {"first_name": "new_first_name"}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{account.id}", headers=HEADERS, data=json.dumps(update_params))

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == account.id
            assert response.json.get("username") == account.username
            assert response.json.get("first_name") == "new_first_name"
            assert response.json.get("last_name") == "old_last_name"

    def test_update_account_profile_last_name_only(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="old_first_name", last_name="old_last_name", password="password", username="username"
            )
        )

        update_params = {"last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{account.id}", headers=HEADERS, data=json.dumps(update_params))

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == account.id
            assert response.json.get("username") == account.username
            assert response.json.get("first_name") == "old_first_name"
            assert response.json.get("last_name") == "new_last_name"

    def test_update_account_profile_both_names(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="old_first_name", last_name="old_last_name", password="password", username="username"
            )
        )

        update_params = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{account.id}", headers=HEADERS, data=json.dumps(update_params))

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == account.id
            assert response.json.get("username") == account.username
            assert response.json.get("first_name") == "new_first_name"
            assert response.json.get("last_name") == "new_last_name"

    def test_update_account_profile_empty_string_values(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="original_first_name",
                last_name="original_last_name",
                password="password",
                username="username",
            )
        )

        update_params = {"first_name": "", "last_name": ""}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{account.id}", headers=HEADERS, data=json.dumps(update_params))

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == account.id
            assert response.json.get("username") == account.username
            assert response.json.get("first_name") == ""
            assert response.json.get("last_name") == ""

    def test_update_account_profile_account_not_found(self) -> None:
        non_existent_account_id = "661e42ec98423703a299a899"
        update_params = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{non_existent_account_id}", headers=HEADERS, data=json.dumps(update_params)
            )

            assert response.status_code == 404
            assert response.json
            assert "message" in response.json
            assert response.json.get("code") == AccountErrorCode.NOT_FOUND
            assert f"We could not find an account with id: {non_existent_account_id}" in response.json.get("message")

    def test_update_account_profile_invalid_object_id(self) -> None:
        invalid_account_id = "invalid_object_id"
        update_params = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{invalid_account_id}", headers=HEADERS, data=json.dumps(update_params)
            )

            assert response.status_code == 500

    def test_delete_account_success(self) -> None:
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

            response = client.delete(
                f"{ACCOUNT_URL}/{account.id}",
                headers={"Authorization": f"Bearer {access_token_response.json.get('token')}"},
            )

            assert response.status_code == 204
            assert response.data == b""

    def test_delete_account_not_found(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        non_existent_account_id = "661e42ec98423703a299a899"

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            response = client.delete(
                f"{ACCOUNT_URL}/{non_existent_account_id}",
                headers={"Authorization": f"Bearer {access_token_response.json.get('token')}"},
            )

            assert response.status_code == 404
            assert response.json
            assert response.json.get("code") == AccountErrorCode.NOT_FOUND
            assert f"We could not find an account with id: {non_existent_account_id}" in response.json.get("message")

    def test_delete_account_without_auth_token(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            response = client.delete(f"{ACCOUNT_URL}/{account.id}")

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_delete_account_with_invalid_token(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            response = client.delete(f"{ACCOUNT_URL}/{account.id}", headers={"Authorization": "Bearer invalid_token"})

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_INVALID

    def test_deleted_account_cannot_be_retrieved(self) -> None:
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

            delete_response = client.delete(
                f"{ACCOUNT_URL}/{account.id}",
                headers={"Authorization": f"Bearer {access_token_response.json.get('token')}"},
            )
            assert delete_response.status_code == 204

            get_response = client.get(
                f"{ACCOUNT_URL}/{account.id}",
                headers={"Authorization": f"Bearer {access_token_response.json.get('token')}"},
            )

            assert get_response.status_code == 404
            assert get_response.json
            assert get_response.json.get("code") == AccountErrorCode.NOT_FOUND

    def test_deleted_account_cannot_login(self) -> None:
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

            delete_response = client.delete(
                f"{ACCOUNT_URL}/{account.id}",
                headers={"Authorization": f"Bearer {access_token_response.json.get('token')}"},
            )
            assert delete_response.status_code == 204

            login_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            assert login_response.status_code == 404
            assert login_response.json
            assert login_response.json.get("code") == AccountErrorCode.NOT_FOUND

    def test_delete_account_invalid_object_id(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        invalid_account_id = "invalid_object_id"

        with app.test_client() as client:
            access_token_response = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

            response = client.delete(
                f"{ACCOUNT_URL}/{invalid_account_id}",
                headers={"Authorization": f"Bearer {access_token_response.json.get('token')}"},
            )

            assert response.status_code == 500
