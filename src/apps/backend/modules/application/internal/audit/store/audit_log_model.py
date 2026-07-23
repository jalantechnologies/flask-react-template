from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from bson import ObjectId

from modules.application.base_model import BaseModel
from modules.application.common.types import ActorType, FieldChange, FieldChanges, ResourceAction


@dataclass
class AuditLogModel(BaseModel):

    resource_type: str
    resource_id: str
    actor_type: ActorType
    actor_id: Optional[str]
    action: ResourceAction
    timestamp: datetime
    changes: FieldChanges = field(default_factory=dict)
    id: Optional[ObjectId | str] = None

    @classmethod
    def from_bson(cls, bson_data: dict[str, Any]) -> "AuditLogModel":
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
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "audit_log"
