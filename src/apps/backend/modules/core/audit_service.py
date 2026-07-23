from typing import Optional

from modules.core.common.types import AuditActor, AuditOutcome, FieldChanges, ResourceAction
from modules.core.internal.audit.audit_writer import AuditWriter


class AuditService:
    @staticmethod
    def record_audit(
        *,
        actor: AuditActor,
        resource_type: str,
        resource_id: str,
        action: ResourceAction,
        changes: Optional[FieldChanges] = None,
        outcome: AuditOutcome = AuditOutcome.SUCCESS,
    ) -> None:
        AuditWriter.record(
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            changes=changes,
            outcome=outcome,
        )
