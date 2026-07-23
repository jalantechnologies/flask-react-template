from typing import Optional

from flask import Flask

from modules.core.common.types import AuditActor, AuditOutcome, FieldChanges, ResourceAction
from modules.core.internal.audit.audit_writer import AuditWriter
from modules.core.internal.security_headers import SecurityHeaders


class ApplicationService:
    @staticmethod
    def install_security_headers(app: Flask) -> None:
        SecurityHeaders.init_app(app)

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
        # Rarely needed: ApplicationRepository already audits every create/update/delete. Use this only
        # for an access a custom reader/writer performs that the generic CRUD does not cover.
        AuditWriter.record(
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            changes=changes,
            outcome=outcome,
        )
