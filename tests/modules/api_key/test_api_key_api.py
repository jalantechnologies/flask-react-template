from datetime import UTC, datetime, timedelta

from modules.api_key.internal.api_key_util import ApiKeyUtil
from modules.api_key.internal.store.api_key_repository import ApiKeyRepository
from modules.api_key.types import ApiKey, ApiKeyErrorCode, ApiKeyKind, ApiKeyQuery, ApiKeyStatus
from modules.authentication.types import AccessTokenErrorCode
from tests.conftest import TEST_ACTOR
from tests.modules.api_key.base_test_api_key import ApiKeyRequestBody, BaseTestApiKey


class TestApiKeyApi(BaseTestApiKey):

    # CREATE

    def test_create_api_key_returns_plaintext_once(self) -> None:
        account, token = self.create_account_and_get_token()

        response = self.create_key_request(account.id, token, data={"name": "Deploy Bot"})

        assert response.status_code == 201
        assert response.json is not None
        assert response.json["name"] == "Deploy Bot"
        assert response.json["status"] == ApiKeyStatus.ACTIVE.value
        assert response.json["account_id"] == account.id
        # The plaintext is shown once at creation and never persisted in readable form.
        assert response.json["key"].startswith("frt_")
        assert "key_hash" not in response.json

    def test_create_api_key_with_expiry(self) -> None:
        account, token = self.create_account_and_get_token()

        response = self.create_key_request(account.id, token, data={"name": "Temp", "expires_in_days": 30})

        assert response.status_code == 201
        assert response.json is not None
        assert response.json["expires_at"] is not None

    def test_create_api_key_missing_name(self) -> None:
        account, token = self.create_account_and_get_token()

        response = self.create_key_request(account.id, token, data=ApiKeyRequestBody())

        self.assert_error_response(response, 400, ApiKeyErrorCode.BAD_REQUEST)

    def test_create_api_key_invalid_expiry(self) -> None:
        account, token = self.create_account_and_get_token()

        response = self.create_key_request(account.id, token, data={"name": "Bad", "expires_in_days": -1})

        self.assert_error_response(response, 400, ApiKeyErrorCode.BAD_REQUEST)

    def test_create_api_key_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()

        response = self.create_key_request(account.id, "", data={"name": "X"})

        assert response.status_code == 401

    # LIST

    def test_list_api_keys_returns_metadata_without_secret(self) -> None:
        account, token = self.create_account_and_get_token()
        self.seed_api_key(account.id, name="Key A")
        self.seed_api_key(account.id, name="Key B")

        response = self.list_keys_request(account.id, token)

        assert response.status_code == 200
        assert response.json is not None
        items = response.json["items"]
        assert len(items) == 2
        for item in items:
            assert "key" not in item
            assert "key_hash" not in item
            assert item["account_id"] == account.id

    def test_list_api_keys_hides_internal_keys(self) -> None:
        account, token = self.create_account_and_get_token()
        self.seed_api_key(account.id, name="User Key")
        # An internal, system-provisioned key owned by the same account must not appear in the UI list.
        ApiKeyRepository.create(self._internal_key_entity(account.id), actor=TEST_ACTOR)

        response = self.list_keys_request(account.id, token)

        assert response.json is not None
        assert len(response.json["items"]) == 1
        assert response.json["items"][0]["name"] == "User Key"

    def test_list_api_keys_is_account_isolated(self) -> None:
        account_a, token_a = self.create_account_and_get_token("a@example.com", "pwd_a")
        account_b, _ = self.create_account_and_get_token("b@example.com", "pwd_b")
        self.seed_api_key(account_b.id, name="B key")

        response = self.list_keys_request(account_a.id, token_a)

        assert response.json is not None
        assert response.json["items"] == []

    def test_list_keys_cross_account_is_unauthorized(self) -> None:
        _account_a, token_a = self.create_account_and_get_token("attacker@example.com", "pwd_a")
        account_b, _ = self.create_account_and_get_token("victim@example.com", "pwd_b")

        response = self.list_keys_request(account_b.id, token_a)

        self.assert_error_response(response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)

    # REVOKE

    def test_revoke_api_key_success(self) -> None:
        account, token = self.create_account_and_get_token()
        seeded = self.seed_api_key(account.id)

        response = self.revoke_key_request(account.id, seeded.api_key.id, token)

        assert response.status_code == 204
        stored = ApiKeyRepository.query_one(self._id_query(seeded.api_key.id), actor=TEST_ACTOR)
        assert stored is not None
        assert stored.status == ApiKeyStatus.REVOKED

    def test_revoke_already_revoked_returns_conflict(self) -> None:
        account, token = self.create_account_and_get_token()
        seeded = self.seed_api_key(account.id)
        self.revoke_key_request(account.id, seeded.api_key.id, token)

        response = self.revoke_key_request(account.id, seeded.api_key.id, token)

        self.assert_error_response(response, 409, ApiKeyErrorCode.ALREADY_REVOKED)

    def test_revoke_not_found(self) -> None:
        account, token = self.create_account_and_get_token()

        response = self.revoke_key_request(account.id, "507f1f77bcf86cd799439011", token)

        self.assert_error_response(response, 404, ApiKeyErrorCode.NOT_FOUND)

    def test_revoke_cross_account_cannot_revoke(self) -> None:
        _account_a, token_a = self.create_account_and_get_token("attacker@example.com", "pwd_a")
        account_b, _ = self.create_account_and_get_token("victim@example.com", "pwd_b")
        seeded = self.seed_api_key(account_b.id)

        response = self.revoke_key_request(account_b.id, seeded.api_key.id, token_a)

        self.assert_error_response(response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)
        stored = ApiKeyRepository.query_one(self._id_query(seeded.api_key.id), actor=TEST_ACTOR)
        assert stored is not None
        assert stored.status == ApiKeyStatus.ACTIVE

    # AUTHENTICATION VIA KEY

    def test_valid_api_key_authenticates_as_owner(self) -> None:
        account, _ = self.create_account_and_get_token()
        seeded = self.seed_api_key(account.id)

        response = self.call_with_bearer(f"http://127.0.0.1:8080/api/accounts/{account.id}", seeded.plaintext_key)

        assert response.status_code == 200
        assert response.json is not None
        assert response.json["id"] == account.id

    def test_api_key_cannot_access_another_account(self) -> None:
        account_a, _ = self.create_account_and_get_token("owner-a@example.com", "pwd_a")
        account_b, _ = self.create_account_and_get_token("owner-b@example.com", "pwd_b")
        seeded = self.seed_api_key(account_a.id)

        response = self.call_with_bearer(f"http://127.0.0.1:8080/api/accounts/{account_b.id}", seeded.plaintext_key)

        self.assert_error_response(response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)

    def test_unknown_api_key_is_rejected(self) -> None:
        account, _ = self.create_account_and_get_token()

        response = self.call_with_bearer(f"http://127.0.0.1:8080/api/accounts/{account.id}", "frt_deadbeef")

        assert response.status_code == 401

    def test_revoked_api_key_is_rejected(self) -> None:
        account, token = self.create_account_and_get_token()
        seeded = self.seed_api_key(account.id)
        self.revoke_key_request(account.id, seeded.api_key.id, token)

        response = self.call_with_bearer(f"http://127.0.0.1:8080/api/accounts/{account.id}", seeded.plaintext_key)

        assert response.status_code == 401

    def test_expired_api_key_is_rejected_and_marked_expired(self) -> None:
        account, _ = self.create_account_and_get_token()
        seeded = self.seed_api_key(account.id)
        # Backdate expiry directly in the store so the key is past due at auth time.
        ApiKeyRepository.collection().update_one(
            {"key_hash": self._hash(seeded.plaintext_key)},
            {"$set": {"expires_at": datetime.now(tz=UTC) - timedelta(days=1)}},
        )

        response = self.call_with_bearer(f"http://127.0.0.1:8080/api/accounts/{account.id}", seeded.plaintext_key)

        self.assert_error_response(response, 401, ApiKeyErrorCode.EXPIRED)
        stored = ApiKeyRepository.query_one(self._id_query(seeded.api_key.id), actor=TEST_ACTOR)
        assert stored is not None
        assert stored.status == ApiKeyStatus.EXPIRED

    def test_authenticated_call_updates_last_used_at(self) -> None:
        account, _ = self.create_account_and_get_token()
        seeded = self.seed_api_key(account.id)
        assert seeded.api_key.last_used_at is None

        self.call_with_bearer(f"http://127.0.0.1:8080/api/accounts/{account.id}", seeded.plaintext_key)

        stored = ApiKeyRepository.query_one(self._id_query(seeded.api_key.id), actor=TEST_ACTOR)
        assert stored is not None
        assert stored.last_used_at is not None

    # HELPERS

    @staticmethod
    def _hash(plaintext: str) -> str:
        return ApiKeyUtil.hash_key(plaintext)

    @staticmethod
    def _id_query(api_key_id: str) -> ApiKeyQuery:
        return ApiKeyQuery(id=api_key_id)

    @staticmethod
    def _internal_key_entity(account_id: str) -> ApiKey:
        return ApiKey(
            id="",
            account_id=account_id,
            name="Internal",
            key_hash=ApiKeyUtil.hash_key("frt_internal_seed"),
            status=ApiKeyStatus.ACTIVE,
            kind=ApiKeyKind.INTERNAL,
        )
