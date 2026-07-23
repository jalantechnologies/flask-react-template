import json
import unittest
from typing import Optional, Tuple, TypedDict

from server import app
from werkzeug.test import TestResponse

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import Account, CreateAccountByUsernameAndPasswordParams
from modules.api_key.api_key_service import ApiKeyService
from modules.api_key.internal.store.api_key_repository import ApiKeyRepository
from modules.api_key.types import CreateApiKeyParams, CreateApiKeyResult
from modules.application.internal.audit.store.audit_log_repository import AuditLogRepository
from tests.conftest import TEST_ACTOR


class ApiKeyRequestBody(TypedDict, total=False):
    name: str
    expires_in_days: Optional[int]


class BaseTestApiKey(unittest.TestCase):
    ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
    HEADERS = {"Content-Type": "application/json"}

    DEFAULT_KEY_NAME = "CI Deploy Bot"
    DEFAULT_PASSWORD = "testpassword"
    DEFAULT_FIRST_NAME = "Test"
    DEFAULT_LAST_NAME = "User"

    def tearDown(self) -> None:
        ApiKeyRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})
        AuditLogRepository.collection().delete_many({})

    # URL HELPERS

    def api_keys_url(self, account_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/api-keys"

    def api_key_by_id_url(self, account_id: str, api_key_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/api-keys/{api_key_id}"

    # ACCOUNT + TOKEN HELPERS

    def create_test_account(self, username: str, password: Optional[str] = None) -> Account:
        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username=username,
                password=password or self.DEFAULT_PASSWORD,
                first_name=self.DEFAULT_FIRST_NAME,
                last_name=self.DEFAULT_LAST_NAME,
            ),
            actor=TEST_ACTOR,
        )

    def get_access_token(self, username: str, password: Optional[str] = None) -> str:
        with app.test_client() as client:
            response = client.post(
                self.ACCESS_TOKEN_URL,
                headers=self.HEADERS,
                data=json.dumps({"username": username, "password": password or self.DEFAULT_PASSWORD}),
            )
            assert response.json is not None
            token = response.json.get("token")
            assert isinstance(token, str)
            return token

    def create_account_and_get_token(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> Tuple[Account, str]:
        test_username = username or f"apikeyuser_{id(self)}@example.com"
        test_password = password or self.DEFAULT_PASSWORD
        account = self.create_test_account(username=test_username, password=test_password)
        token = self.get_access_token(username=test_username, password=test_password)
        return account, token

    # KEY SEEDING (arrange phase — actor is the test actor, never the view's)

    def seed_api_key(
        self, account_id: str, name: Optional[str] = None, expires_in_days: Optional[int] = None
    ) -> CreateApiKeyResult:
        return ApiKeyService.create_api_key(
            params=CreateApiKeyParams(
                account_id=account_id, name=name or self.DEFAULT_KEY_NAME, expires_in_days=expires_in_days
            ),
            actor=TEST_ACTOR,
        )

    # HTTP HELPERS

    def create_key_request(self, account_id: str, token: str, data: Optional[ApiKeyRequestBody] = None) -> TestResponse:
        with app.test_client() as client:
            return client.post(
                self.api_keys_url(account_id),
                headers={**self.HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(data) if data is not None else None,
            )

    def list_keys_request(self, account_id: str, token: str) -> TestResponse:
        with app.test_client() as client:
            return client.get(self.api_keys_url(account_id), headers={"Authorization": f"Bearer {token}"})

    def revoke_key_request(self, account_id: str, api_key_id: str, token: str) -> TestResponse:
        with app.test_client() as client:
            return client.delete(
                self.api_key_by_id_url(account_id, api_key_id), headers={"Authorization": f"Bearer {token}"}
            )

    def call_with_bearer(self, url: str, bearer: str) -> TestResponse:
        with app.test_client() as client:
            return client.get(url, headers={"Authorization": f"Bearer {bearer}"})

    def assert_error_response(self, response: TestResponse, expected_status: int, expected_code: str) -> None:
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        assert response.json is not None
        assert response.json.get("code") == expected_code, f"Expected {expected_code}, got {response.json.get('code')}"
