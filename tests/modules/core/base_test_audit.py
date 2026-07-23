import unittest
from typing import Any, Callable

from modules.account.internal.store.account_repository import AccountRepository
from modules.core.common.types import ActorType, AuditActor
from modules.core.internal.audit.store.audit_log_repository import AuditLogRepository


class BaseTestAudit(unittest.TestCase):
    ACTOR = AuditActor(actor_type=ActorType.ACCOUNT, actor_id="tester")

    def setup_method(self, method: Callable[..., object]) -> None:
        AuditLogRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    def teardown_method(self, method: Callable[..., object]) -> None:
        AuditLogRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    @staticmethod
    def audit_docs() -> list[dict[str, Any]]:
        return list(AuditLogRepository.collection().find({}))
