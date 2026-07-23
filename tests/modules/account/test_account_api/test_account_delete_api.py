from server import app

from modules.account.account_service import AccountService
from modules.account.errors import AccountWithUsernameNotFoundError
from modules.account.types import AccountErrorCode, AccountSearchParams, CreateAccountByUsernameAndPasswordParams
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import AccessTokenErrorCode
from tests.conftest import TEST_ACTOR
from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"


class TestAccountDeleteApi(BaseTestAccount):
    def test_given_authenticated_account_when_deleting_own_account_then_returns_no_content(self) -> None:
        with app.test_client() as client:
            response = client.delete(
                f"{ACCOUNT_URL}/{self.account.id}", headers={"Authorization": f"Bearer {self.access_token.token}"}
            )

            assert response.status_code == 204
            assert response.data == b""

    def test_given_already_deleted_account_when_deleting_it_again_then_returns_not_found(self) -> None:
        authorization_headers = {"Authorization": f"Bearer {self.access_token.token}"}

        with app.test_client() as client:
            first_delete_response = client.delete(f"{ACCOUNT_URL}/{self.account.id}", headers=authorization_headers)
            assert first_delete_response.status_code == 204

            second_delete_response = client.delete(f"{ACCOUNT_URL}/{self.account.id}", headers=authorization_headers)

            assert second_delete_response.status_code == 404
            assert second_delete_response.json
            assert second_delete_response.json.get("code") == AccountErrorCode.NOT_FOUND
            assert f"We could not find an account with id: {self.account.id}" in second_delete_response.json.get(
                "message"
            )

    def test_given_no_authorization_header_when_deleting_account_then_returns_unauthorized(self) -> None:
        with app.test_client() as client:
            response = client.delete(f"{ACCOUNT_URL}/{self.account.id}")

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_given_invalid_access_token_when_deleting_account_then_returns_unauthorized(self) -> None:
        with app.test_client() as client:
            response = client.delete(
                f"{ACCOUNT_URL}/{self.account.id}", headers={"Authorization": "Bearer invalid_token"}
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_INVALID

    def test_given_deleted_account_when_retrieving_it_then_returns_not_found(self) -> None:
        authorization_headers = {"Authorization": f"Bearer {self.access_token.token}"}

        with app.test_client() as client:
            delete_response = client.delete(f"{ACCOUNT_URL}/{self.account.id}", headers=authorization_headers)
            assert delete_response.status_code == 204

            get_response = client.get(f"{ACCOUNT_URL}/{self.account.id}", headers=authorization_headers)

            assert get_response.status_code == 404
            assert get_response.json
            assert get_response.json.get("code") == AccountErrorCode.NOT_FOUND

    def test_given_deleted_account_when_authenticating_then_raises_account_not_found(self) -> None:
        with app.test_client() as client:
            delete_response = client.delete(
                f"{ACCOUNT_URL}/{self.account.id}", headers={"Authorization": f"Bearer {self.access_token.token}"}
            )
            assert delete_response.status_code == 204

        with self.assertRaises(AccountWithUsernameNotFoundError):
            AccountService.get_account_by_username_and_password(
                params=AccountSearchParams(password="password", username=self.account.username)
            )

    def test_given_malformed_account_id_when_deleting_account_then_returns_unauthorized(self) -> None:
        malformed_account_id = "invalid_object_id"

        with app.test_client() as client:
            response = client.delete(
                f"{ACCOUNT_URL}/{malformed_account_id}", headers={"Authorization": f"Bearer {self.access_token.token}"}
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.UNAUTHORIZED_ACCESS

    def test_given_authenticated_account_when_deleting_another_users_account_then_returns_unauthorized(self) -> None:
        other_account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="other_first_name", last_name="other_last_name", password="password", username="other_user"
            ),
            actor=TEST_ACTOR,
        )
        other_account_token = AuthenticationService.create_access_token_by_username_and_password(account=other_account)

        with app.test_client() as client:
            delete_response = client.delete(
                f"{ACCOUNT_URL}/{other_account.id}", headers={"Authorization": f"Bearer {self.access_token.token}"}
            )

            assert delete_response.status_code == 401
            assert delete_response.json
            assert delete_response.json.get("code") == AccessTokenErrorCode.UNAUTHORIZED_ACCESS

            get_response = client.get(
                f"{ACCOUNT_URL}/{other_account.id}", headers={"Authorization": f"Bearer {other_account_token.token}"}
            )
            assert get_response.status_code == 200
