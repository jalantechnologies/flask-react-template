import json

from server import app

from modules.account.account_service import AccountService
from modules.account.types import AccountErrorCode, CreateAccountByUsernameAndPasswordParams
from modules.authentication.types import AccessTokenErrorCode
from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
HEADERS = {"Content-Type": "application/json"}


class TestAccountPatchApi(BaseTestAccount):
    def test_given_account_when_updating_only_first_name_then_returns_updated_account(self) -> None:
        request_body = {"first_name": "new_first_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(request_body),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == self.account.id
            assert response.json.get("username") == self.account.username
            assert response.json.get("first_name") == "new_first_name"
            assert response.json.get("last_name") == self.account.last_name

    def test_given_account_when_updating_only_last_name_then_returns_updated_account(self) -> None:
        request_body = {"last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(request_body),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == self.account.id
            assert response.json.get("username") == self.account.username
            assert response.json.get("first_name") == self.account.first_name
            assert response.json.get("last_name") == "new_last_name"

    def test_given_account_when_updating_first_and_last_name_then_returns_updated_account(self) -> None:
        request_body = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(request_body),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == self.account.id
            assert response.json.get("username") == self.account.username
            assert response.json.get("first_name") == "new_first_name"
            assert response.json.get("last_name") == "new_last_name"

    def test_given_account_when_updating_names_to_empty_strings_then_returns_updated_account(self) -> None:
        request_body = {"first_name": "", "last_name": ""}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(request_body),
            )

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == self.account.id
            assert response.json.get("username") == self.account.username
            assert response.json.get("first_name") == ""
            assert response.json.get("last_name") == ""

    def test_given_no_authorization_header_when_updating_profile_then_returns_unauthorized(self) -> None:
        request_body = {"first_name": "new_first_name"}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps(request_body))

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_given_invalid_access_token_when_updating_profile_then_returns_unauthorized(self) -> None:
        request_body = {"first_name": "new_first_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}",
                headers={**HEADERS, "Authorization": "Bearer invalid_token"},
                data=json.dumps(request_body),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_INVALID

    def test_given_authorization_header_without_a_token_when_updating_profile_then_returns_unauthorized(self) -> None:
        request_body = {"first_name": "new_first_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}",
                headers={**HEADERS, "Authorization": "Bearer"},
                data=json.dumps(request_body),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.INVALID_AUTHORIZATION_HEADER

    def test_given_authorization_header_with_extra_whitespace_when_updating_profile_then_returns_unauthorized(
        self,
    ) -> None:
        request_body = {"first_name": "new_first_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{self.account.id}",
                headers={**HEADERS, "Authorization": f"Bearer  {self.access_token.token}"},
                data=json.dumps(request_body),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.INVALID_AUTHORIZATION_HEADER

    def test_given_authenticated_account_when_updating_another_users_profile_then_returns_unauthorized(self) -> None:
        other_account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="other_first_name", last_name="other_last_name", password="password", username="other_user"
            )
        )
        request_body = {"first_name": "new_first_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{other_account.id}",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(request_body),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.UNAUTHORIZED_ACCESS

    def test_given_authenticated_account_when_updating_a_nonexistent_account_then_returns_unauthorized(self) -> None:
        nonexistent_account_id = "661e42ec98423703a299a899"
        request_body = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{nonexistent_account_id}",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(request_body),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.UNAUTHORIZED_ACCESS

    def test_given_authenticated_account_when_updating_a_malformed_account_id_then_returns_unauthorized(self) -> None:
        malformed_account_id = "invalid_object_id"
        request_body = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{malformed_account_id}",
                headers={**HEADERS, "Authorization": f"Bearer {self.access_token.token}"},
                data=json.dumps(request_body),
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.UNAUTHORIZED_ACCESS

    def test_given_unrecognized_request_body_when_updating_profile_then_returns_bad_request(self) -> None:
        request_body = {"unexpected_field": "value"}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps(request_body))

            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == AccountErrorCode.BAD_REQUEST

    def test_given_null_request_body_when_updating_profile_then_returns_bad_request(self) -> None:
        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps(None))

            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == AccountErrorCode.BAD_REQUEST

    def test_given_numeric_request_body_when_updating_profile_then_returns_bad_request(self) -> None:
        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps(123))

            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == AccountErrorCode.BAD_REQUEST

    def test_given_string_request_body_when_updating_profile_then_returns_bad_request(self) -> None:
        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps("first_name"))

            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == AccountErrorCode.BAD_REQUEST

    def test_given_reset_password_body_with_extra_keys_when_resetting_password_then_returns_not_found(self) -> None:
        request_body = {"extra": "value", "new_password": "new_password", "token": "token"}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps(request_body))

            assert response.status_code == 404
