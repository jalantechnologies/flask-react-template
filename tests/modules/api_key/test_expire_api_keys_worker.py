from datetime import UTC, datetime, timedelta

from modules.account.internal.store.account_repository import AccountRepository
from modules.api_key.internal.store.api_key_repository import ApiKeyRepository
from modules.api_key.internal.workers.expire_api_keys_worker import ExpireApiKeysWorker
from modules.api_key.types import ApiKeyQuery, ApiKeyStatus
from modules.application.internal.audit.store.audit_log_repository import AuditLogRepository
from tests.conftest import TEST_ACTOR
from tests.modules.api_key.base_test_api_key import BaseTestApiKey


class TestExpireApiKeysWorker(BaseTestApiKey):

    def _set_expiry(self, key_hash: str, expires_at: datetime) -> None:
        ApiKeyRepository.collection().update_one({"key_hash": key_hash}, {"$set": {"expires_at": expires_at}})

    def _status(self, api_key_id: str) -> ApiKeyStatus:
        stored = ApiKeyRepository.query_one(ApiKeyQuery(id=api_key_id), actor=TEST_ACTOR)
        assert stored is not None
        return stored.status

    def test_worker_expires_only_past_due_active_keys(self) -> None:
        account = self.create_test_account("worker-owner@example.com")

        past = self.seed_api_key(account.id, name="Past Due")
        future = self.seed_api_key(account.id, name="Still Valid")
        no_expiry = self.seed_api_key(account.id, name="No Expiry")

        self._set_expiry(past.api_key.key_hash, datetime.now(tz=UTC) - timedelta(days=1))
        self._set_expiry(future.api_key.key_hash, datetime.now(tz=UTC) + timedelta(days=30))

        ExpireApiKeysWorker.perform()

        assert self._status(past.api_key.id) == ApiKeyStatus.EXPIRED
        assert self._status(future.api_key.id) == ApiKeyStatus.ACTIVE
        assert self._status(no_expiry.api_key.id) == ApiKeyStatus.ACTIVE

    def test_worker_is_a_noop_when_nothing_expired(self) -> None:
        account = self.create_test_account("worker-owner2@example.com")
        active = self.seed_api_key(account.id, name="Active")

        ExpireApiKeysWorker.perform()

        assert self._status(active.api_key.id) == ApiKeyStatus.ACTIVE

    def test_worker_records_an_audit_entry_for_each_expiry(self) -> None:
        account = self.create_test_account("worker-owner3@example.com")
        AuditLogRepository.collection().delete_many({})
        past = self.seed_api_key(account.id, name="Past Due")
        self._set_expiry(past.api_key.key_hash, datetime.now(tz=UTC) - timedelta(days=1))

        ExpireApiKeysWorker.perform()

        update_entries = [
            doc
            for doc in AuditLogRepository.collection().find({})
            if doc["resource_type"] == "api_keys"
            and doc["resource_id"] == past.api_key.id
            and doc["action"] == "update"
        ]
        assert len(update_entries) >= 1
        assert update_entries[-1]["actor_type"] == "worker"

    def test_worker_configuration(self) -> None:
        assert ExpireApiKeysWorker.queue == "default"
        assert ExpireApiKeysWorker.max_retries == 1
        assert ExpireApiKeysWorker.cron_schedule == "0 0 * * *"

    def teardown_method(self, method: object) -> None:
        ApiKeyRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})
        AuditLogRepository.collection().delete_many({})
