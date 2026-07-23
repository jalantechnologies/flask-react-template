from datetime import datetime, timezone
from typing import Optional

from modules.application.common.types import (
    REDACTED,
    AuditActor,
    AuditLogEntry,
    AuditRecord,
    FieldChange,
    FieldChanges,
    ResourceAction,
)
from modules.application.internal.audit.store.audit_log_repository import AuditLogRepository
from modules.logger.logger import Logger

SENSITIVE_FIELD_KEYWORDS = ("password", "token", "secret", "otp", "mfa", "hashed")


class AuditWriter:
    @staticmethod
    def record(
        *,
        actor: AuditActor,
        resource_type: str,
        resource_id: str,
        action: ResourceAction,
        changes: Optional[FieldChanges] = None,
    ) -> None:
        record = AuditRecord(
            resource_type=resource_type,
            resource_id=resource_id,
            actor_type=actor.actor_type,
            actor_id=actor.actor_id,
            action=action,
            timestamp=datetime.now(tz=timezone.utc),
            changes=AuditWriter._redact(changes or {}),
        )
        AuditWriter._persist(record)

    @staticmethod
    def _persist(record: AuditRecord) -> None:
        # A failed audit write is logged, not raised: the mutation the caller made has already committed,
        # so failing here would break the caller's success path for a write that already landed (and could
        # not un-apply it). Audit persistence is best-effort; a lost entry is surfaced via the error log.
        try:
            AuditLogRepository.create(
                AuditLogEntry(
                    id="",
                    resource_type=record.resource_type,
                    resource_id=record.resource_id,
                    actor_type=record.actor_type,
                    actor_id=record.actor_id,
                    action=record.action,
                    timestamp=record.timestamp,
                    changes=record.changes,
                )
            )
        except Exception as exc:
            Logger.error(
                message=f"audit log write failed for {record.action.value} on "
                f"{record.resource_type}:{record.resource_id}: {exc}"
            )

    @staticmethod
    def _redact(changes: FieldChanges) -> FieldChanges:
        return {name: AuditWriter._redact_change(name, change) for name, change in changes.items()}

    @staticmethod
    def _redact_change(field_name: str, change: FieldChange) -> FieldChange:
        if AuditWriter._is_sensitive(field_name):
            return FieldChange(old=REDACTED, new=REDACTED)
        return change

    @staticmethod
    def _is_sensitive(field_name: str) -> bool:
        lowered = field_name.lower()
        return any(keyword in lowered for keyword in SENSITIVE_FIELD_KEYWORDS)
