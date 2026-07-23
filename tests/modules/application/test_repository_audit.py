from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import Account, AccountQuery
from modules.application.common.types import ActorType, AuditActor, ResourceAction
from tests.modules.application.base_test_audit import BaseTestAudit


class TestRepositoryAudit(BaseTestAudit):
    def _make_account(self) -> Account:
        return Account(
            id="",
            first_name="first",
            last_name="last",
            hashed_password="hashed",
            phone_number=None,
            username="user@example.com",
        )

    def test_create_records_a_create_entry_for_the_actor(self) -> None:
        created = AccountRepository.create(self._make_account(), actor=self.ACTOR)

        docs = self.audit_docs()
        assert len(docs) == 1
        entry = docs[0]
        assert entry["resource_type"] == AccountRepository.collection_name
        assert entry["resource_id"] == created.id
        assert entry["action"] == ResourceAction.CREATE.value
        assert entry["actor_type"] == ActorType.ACCOUNT.value
        assert entry["actor_id"] == "tester"

    def test_update_records_changed_fields_with_old_and_new_values(self) -> None:
        created = AccountRepository.create(self._make_account(), actor=self.ACTOR)

        AccountRepository.update(created.id, {"first_name": "updated"}, actor=self.ACTOR)

        update_entries = [d for d in self.audit_docs() if d["action"] == ResourceAction.UPDATE.value]
        assert len(update_entries) == 1
        changes = update_entries[0]["changes"]
        assert changes["first_name"]["old"] == "first"
        assert changes["first_name"]["new"] == "updated"

    def test_update_redacts_sensitive_field_values(self) -> None:
        created = AccountRepository.create(self._make_account(), actor=self.ACTOR)

        AccountRepository.update(created.id, {"hashed_password": "new-secret"}, actor=self.ACTOR)

        update_entries = [d for d in self.audit_docs() if d["action"] == ResourceAction.UPDATE.value]
        assert len(update_entries) == 1
        changes = update_entries[0]["changes"]
        assert changes["hashed_password"]["old"] == "[redacted]"
        assert changes["hashed_password"]["new"] == "[redacted]"

    def test_delete_records_a_delete_entry(self) -> None:
        created = AccountRepository.create(self._make_account(), actor=self.ACTOR)

        AccountRepository.delete(created.id, actor=self.ACTOR)

        delete_entries = [d for d in self.audit_docs() if d["action"] == ResourceAction.DELETE.value]
        assert len(delete_entries) == 1
        assert delete_entries[0]["resource_id"] == created.id

    def test_worker_actor_is_recorded_when_passed_a_worker_actor(self) -> None:
        worker_actor = AuditActor(actor_type=ActorType.WORKER, actor_id="a_worker")
        AccountRepository.create(self._make_account(), actor=worker_actor)

        docs = self.audit_docs()
        assert len(docs) == 1
        assert docs[0]["actor_type"] == ActorType.WORKER.value
        assert docs[0]["actor_id"] == "a_worker"

    def test_anonymous_actor_is_recorded_with_a_null_actor_id(self) -> None:
        anonymous_actor = AuditActor(actor_type=ActorType.ANONYMOUS, actor_id=None)
        AccountRepository.create(self._make_account(), actor=anonymous_actor)

        docs = self.audit_docs()
        assert len(docs) == 1
        assert docs[0]["actor_type"] == ActorType.ANONYMOUS.value
        assert docs[0]["actor_id"] is None

    def test_audit_writes_do_not_recurse(self) -> None:
        AccountRepository.create(self._make_account(), actor=self.ACTOR)

        assert len(self.audit_docs()) == 1

    def test_find_records_a_read_entry(self) -> None:
        created = AccountRepository.create(self._make_account(), actor=self.ACTOR)

        AccountRepository.find(created.id, actor=self.ACTOR)

        read_entries = [d for d in self.audit_docs() if d["action"] == ResourceAction.READ.value]
        assert len(read_entries) == 1
        assert read_entries[0]["resource_id"] == created.id
        assert read_entries[0]["actor_id"] == "tester"

    def test_query_records_one_read_entry_per_returned_document(self) -> None:
        first = AccountRepository.create(self._make_account_with_username("one@example.com"), actor=self.ACTOR)
        second = AccountRepository.create(self._make_account_with_username("two@example.com"), actor=self.ACTOR)

        results = AccountRepository.query(AccountQuery(), actor=self.ACTOR)
        assert len(results) == 2

        read_entries = [d for d in self.audit_docs() if d["action"] == ResourceAction.READ.value]
        assert len(read_entries) == 2
        assert {entry["resource_id"] for entry in read_entries} == {first.id, second.id}

    def _make_account_with_username(self, username: str) -> Account:
        account = self._make_account()
        return Account(
            id=account.id,
            first_name=account.first_name,
            last_name=account.last_name,
            hashed_password=account.hashed_password,
            phone_number=account.phone_number,
            username=username,
        )
