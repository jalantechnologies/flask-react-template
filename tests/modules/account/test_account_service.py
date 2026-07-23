import json

from server import app

from modules.account.account_service import AccountService
from modules.account.internal.account_writer import AccountWriter
from modules.account.types import (
    AccountErrorCode,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams
from tests.conftest import TEST_ACTOR
from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestAccountService(BaseTestAccount):
    def _create_account_and_get_token(self, username: str, password: str) -> tuple[str, str]:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password=password, username=username
            ),
            actor=TEST_ACTOR,
        )
        token = AuthenticationService.create_access_token_by_username_and_password(account=account).token
        return account.id, token

    def _create_phone_account_and_get_token(self, phone_number: dict[str, str]) -> tuple[str, str]:
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number)), actor=TEST_ACTOR
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

    def test_create_account_by_username_and_password(self) -> None:
        request_body = {
            "first_name": "first_name",
            "last_name": "last_name",
            "password": "password",
            "username": "username",
        }

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=json.dumps(request_body))

        assert response.status_code == 201
        assert response.json is not None
        assert response.json.get("username") == "username"
        assert response.json.get("first_name") == "first_name"
        assert response.json.get("last_name") == "last_name"

    def test_get_account_by_id(self) -> None:
        account_id, token = self._create_account_and_get_token("username", "password")

        with app.test_client() as client:
            response = client.get(f"{ACCOUNT_URL}/{account_id}", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("id") == account_id
        assert response.json.get("username") == "username"
        assert response.json.get("first_name") == "first_name"
        assert response.json.get("last_name") == "last_name"

    def test_get_account_by_id_when_account_deleted_returns_not_found(self) -> None:
        account_id, token = self._create_account_and_get_token("username", "password")
        authorization_headers = {"Authorization": f"Bearer {token}"}

        with app.test_client() as client:
            delete_response = client.delete(f"{ACCOUNT_URL}/{account_id}", headers=authorization_headers)
            assert delete_response.status_code == 204

            response = client.get(f"{ACCOUNT_URL}/{account_id}", headers=authorization_headers)

        assert response.status_code == 404
        assert response.json is not None
        assert response.json.get("code") == AccountErrorCode.NOT_FOUND

    def test_get_or_create_account_by_phone_number(self) -> None:
        request_body = {"phone_number": {"country_code": "+91", "phone_number": "9999999999"}}

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=json.dumps(request_body))

        assert response.status_code == 201
        assert response.json is not None
        assert response.json.get("phone_number") == {"country_code": "+91", "phone_number": "9999999999"}

    def test_login_with_unknown_phone_number_returns_not_found(self) -> None:
        request_body = {"phone_number": {"country_code": "+91", "phone_number": "9999999999"}, "otp_code": "123456"}

        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=json.dumps(request_body))

        assert response.status_code == 404
        assert response.json is not None
        assert response.json.get("code") == AccountErrorCode.NOT_FOUND

    def test_update_account_profile_first_name_only(self) -> None:
        account_id, token = self._create_account_and_get_token("username", "password")
        request_body = {"first_name": "new_first_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(request_body),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("id") == account_id
        assert response.json.get("username") == "username"
        assert response.json.get("first_name") == "new_first_name"
        assert response.json.get("last_name") == "last_name"

    def test_update_account_profile_last_name_only(self) -> None:
        account_id, token = self._create_account_and_get_token("username", "password")
        request_body = {"last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(request_body),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("id") == account_id
        assert response.json.get("username") == "username"
        assert response.json.get("first_name") == "first_name"
        assert response.json.get("last_name") == "new_last_name"

    def test_update_account_profile_both_names(self) -> None:
        account_id, token = self._create_account_and_get_token("username", "password")
        request_body = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(request_body),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("id") == account_id
        assert response.json.get("username") == "username"
        assert response.json.get("first_name") == "new_first_name"
        assert response.json.get("last_name") == "new_last_name"

    def test_update_account_profile_no_changes(self) -> None:
        account_id, token = self._create_account_and_get_token("username", "password")
        request_body = {"first_name": None, "last_name": None}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(request_body),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("id") == account_id
        assert response.json.get("username") == "username"
        assert response.json.get("first_name") == "first_name"
        assert response.json.get("last_name") == "last_name"

    def test_update_account_profile_empty_string_values(self) -> None:
        account_id, token = self._create_account_and_get_token("username", "password")
        request_body = {"first_name": "", "last_name": ""}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(request_body),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("id") == account_id
        assert response.json.get("username") == "username"
        assert response.json.get("first_name") == ""
        assert response.json.get("last_name") == ""

    def test_update_account_profile_nonexistent_account_returns_unauthorized(self) -> None:
        _, token = self._create_account_and_get_token("username", "password")
        nonexistent_account_id = "5f7b1b7b4f3b9b1b3f3b9b1b"
        request_body = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{nonexistent_account_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(request_body),
            )

        assert response.status_code == 401

    def test_update_account_profile_with_phone_number_account(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account_id, token = self._create_phone_account_and_get_token(phone_number)
        request_body = {"first_name": "Phone", "last_name": "User"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{account_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(request_body),
            )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("id") == account_id
        assert response.json.get("phone_number") == phone_number
        assert response.json.get("first_name") == "Phone"
        assert response.json.get("last_name") == "User"

    def test_delete_account_success(self) -> None:
        account_id, token = self._create_account_and_get_token("username", "password")

        with app.test_client() as client:
            response = client.delete(f"{ACCOUNT_URL}/{account_id}", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 204
        assert response.data == b""

    def test_delete_account_not_found(self) -> None:
        _, token = self._create_account_and_get_token("username", "password")
        nonexistent_account_id = "5f7b1b7b4f3b9b1b3f3b9b1b"

        with app.test_client() as client:
            response = client.delete(
                f"{ACCOUNT_URL}/{nonexistent_account_id}", headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 401

    def test_deleted_account_login_returns_invalid_credentials(self) -> None:
        account_id, token = self._create_account_and_get_token("username", "password")

        with app.test_client() as client:
            delete_response = client.delete(f"{ACCOUNT_URL}/{account_id}", headers={"Authorization": f"Bearer {token}"})
            assert delete_response.status_code == 204

            login_response = client.post(
                ACCESS_TOKEN_URL, headers=HEADERS, data=json.dumps({"username": "username", "password": "password"})
            )

        assert login_response.status_code == 401
        assert login_response.json is not None
        assert login_response.json.get("code") == AccountErrorCode.INVALID_CREDENTIALS

    def test_deleted_account_not_found_by_id(self) -> None:
        account_id, token = self._create_account_and_get_token("username", "password")
        authorization_headers = {"Authorization": f"Bearer {token}"}

        with app.test_client() as client:
            delete_response = client.delete(f"{ACCOUNT_URL}/{account_id}", headers=authorization_headers)
            assert delete_response.status_code == 204

            get_response = client.get(f"{ACCOUNT_URL}/{account_id}", headers=authorization_headers)

        assert get_response.status_code == 404
        assert get_response.json is not None
        assert get_response.json.get("code") == AccountErrorCode.NOT_FOUND

    def test_deleted_phone_number_account_not_found(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account_id, token = self._create_phone_account_and_get_token(phone_number)

        with app.test_client() as client:
            delete_response = client.delete(f"{ACCOUNT_URL}/{account_id}", headers={"Authorization": f"Bearer {token}"})
            assert delete_response.status_code == 204

            get_response = client.get(f"{ACCOUNT_URL}/{account_id}", headers={"Authorization": f"Bearer {token}"})

        assert get_response.status_code == 404
        assert get_response.json is not None
        assert get_response.json.get("code") == AccountErrorCode.NOT_FOUND

    def test_can_create_new_account_with_same_username_after_deletion(self) -> None:
        original_account_id, token = self._create_account_and_get_token("username", "password")

        with app.test_client() as client:
            delete_response = client.delete(
                f"{ACCOUNT_URL}/{original_account_id}", headers={"Authorization": f"Bearer {token}"}
            )
            assert delete_response.status_code == 204

            create_response = client.post(
                ACCOUNT_URL,
                headers=HEADERS,
                data=json.dumps(
                    {
                        "first_name": "new_first_name",
                        "last_name": "new_last_name",
                        "password": "new_password",
                        "username": "username",
                    }
                ),
            )

        assert create_response.status_code == 201
        assert create_response.json is not None
        assert create_response.json.get("username") == "username"
        assert create_response.json.get("first_name") == "new_first_name"
        assert create_response.json.get("id") != original_account_id

    def test_can_create_new_account_with_same_phone_number_after_deletion(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        original_account_id, token = self._create_phone_account_and_get_token(phone_number)

        with app.test_client() as client:
            delete_response = client.delete(
                f"{ACCOUNT_URL}/{original_account_id}", headers={"Authorization": f"Bearer {token}"}
            )
            assert delete_response.status_code == 204

            create_response = client.post(ACCOUNT_URL, headers=HEADERS, data=json.dumps({"phone_number": phone_number}))

        assert create_response.status_code == 201
        assert create_response.json is not None
        assert create_response.json.get("phone_number") == phone_number
        assert create_response.json.get("id") != original_account_id
