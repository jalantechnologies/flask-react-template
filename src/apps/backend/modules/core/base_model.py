from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping, NotRequired, Optional, TypedDict

from bson import ObjectId

type StoredDocument = dict[str, Any]


class StoredDocumentBase(TypedDict):
    _id: NotRequired[ObjectId]
    created_at: NotRequired[Optional[datetime]]
    updated_at: NotRequired[Optional[datetime]]


@dataclass(kw_only=True)
class BaseModel:
    created_at: Optional[datetime] = field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.created_at is not None and self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=UTC)
        if self.updated_at is None:
            self.updated_at = self.created_at
        elif self.updated_at.tzinfo is None:
            self.updated_at = self.updated_at.replace(tzinfo=UTC)

    def to_bson(self) -> Mapping[str, Any]:
        data = asdict(self)
        if data.get("id") is not None:
            data["_id"] = data.pop("id")
        else:
            data.pop("id", None)
        return data
