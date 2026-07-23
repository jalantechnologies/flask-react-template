from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, NotRequired, Optional, TypedDict

from bson import ObjectId

from modules.core.base_model import BaseModel, StoredDocument, StoredDocumentBase
from modules.core.common.types import ActorType, AuditOutcome, FieldChange, FieldChanges, ResourceAction


class AuditLogChangeDocument(TypedDict):
    old: Any
    new: Any


class AuditLogDocument(StoredDocumentBase):
    resource_type: str
    resource_id: str
    actor_type: str
    actor_id: Optional[str]
    action: str
    timestamp: datetime
    changes: NotRequired[Optional[dict[str, AuditLogChangeDocument]]]
    outcome: NotRequired[str]


@dataclass
class AuditLogModel(BaseModel):

    resource_type: str
    resource_id: str
    actor_type: ActorType
    actor_id: Optional[str]
    action: ResourceAction
    timestamp: datetime
    changes: FieldChanges = field(default_factory=dict)
    outcome: AuditOutcome = AuditOutcome.SUCCESS
    id: Optional[ObjectId | str] = None

    @classmethod
    def from_bson(cls, bson_data: StoredDocument) -> "AuditLogModel":
        raw_changes = bson_data.get("changes") or {}
        return cls(
            id=bson_data.get("_id"),
            resource_type=bson_data["resource_type"],
            resource_id=bson_data["resource_id"],
            actor_type=ActorType(bson_data["actor_type"]),
            actor_id=bson_data.get("actor_id"),
            action=ResourceAction(bson_data["action"]),
            timestamp=bson_data["timestamp"],
            changes={
                name: FieldChange(old=value.get("old"), new=value.get("new")) for name, value in raw_changes.items()
            },
            outcome=AuditOutcome(bson_data.get("outcome", AuditOutcome.SUCCESS.value)),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "audit_log"
