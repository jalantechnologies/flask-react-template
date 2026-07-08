import json

from server import app

from modules.account.types import AccountErrorCode
from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
HEADERS = {"Content-Type": "application/json"}


class TestAccountPatchApi(BaseTestAccount):
    def test_given_account_when_updating_only_first_name_then_returns_updated_account(self) -> None:
        request_body = {"first_name": "new_first_name"}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps(request_body))

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == self.account.id
            assert response.json.get("username") == self.account.username
            assert response.json.get("first_name") == "new_first_name"
            assert response.json.get("last_name") == self.account.last_name

    def test_given_account_when_updating_only_last_name_then_returns_updated_account(self) -> None:
        request_body = {"last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps(request_body))

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == self.account.id
            assert response.json.get("username") == self.account.username
            assert response.json.get("first_name") == self.account.first_name
            assert response.json.get("last_name") == "new_last_name"

    def test_given_account_when_updating_first_and_last_name_then_returns_updated_account(self) -> None:
        request_body = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps(request_body))

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == self.account.id
            assert response.json.get("username") == self.account.username
            assert response.json.get("first_name") == "new_first_name"
            assert response.json.get("last_name") == "new_last_name"

    def test_given_account_when_updating_names_to_empty_strings_then_returns_updated_account(self) -> None:
        request_body = {"first_name": "", "last_name": ""}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps(request_body))

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == self.account.id
            assert response.json.get("username") == self.account.username
            assert response.json.get("first_name") == ""
            assert response.json.get("last_name") == ""

    def test_given_unrecognized_request_body_when_updating_profile_then_returns_bad_request(self) -> None:
        request_body = {"unexpected_field": "value"}

        with app.test_client() as client:
            response = client.patch(f"{ACCOUNT_URL}/{self.account.id}", headers=HEADERS, data=json.dumps(request_body))

            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == AccountErrorCode.BAD_REQUEST

    def test_given_nonexistent_account_id_when_updating_profile_then_returns_not_found(self) -> None:
        nonexistent_account_id = "661e42ec98423703a299a899"
        request_body = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{nonexistent_account_id}", headers=HEADERS, data=json.dumps(request_body)
            )

            assert response.status_code == 404
            assert response.json
            assert response.json.get("code") == AccountErrorCode.NOT_FOUND
            assert f"We could not find an account with id: {nonexistent_account_id}" in response.json.get("message")

    def test_given_malformed_account_id_when_updating_profile_then_returns_not_found(self) -> None:
        malformed_account_id = "invalid_object_id"
        request_body = {"first_name": "new_first_name", "last_name": "new_last_name"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_URL}/{malformed_account_id}", headers=HEADERS, data=json.dumps(request_body)
            )

            assert response.status_code == 404
