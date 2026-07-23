from dataclasses import dataclass, field
from datetime import datetime
from typing import NotRequired, Optional

from bson import ObjectId

from modules.core.base_model import BaseModel, StoredDocument, StoredDocumentBase
from modules.core.common.types import JobArguments, JobRunStatus


class JobRunDocument(StoredDocumentBase):
    job_name: NotRequired[str]
    status: NotRequired[str]
    arguments: NotRequired[JobArguments]
    retry_count: NotRequired[int]
    started_at: NotRequired[Optional[datetime]]
    ended_at: NotRequired[Optional[datetime]]


@dataclass
class JobRunModel(BaseModel):
    job_name: str
    status: JobRunStatus
    arguments: JobArguments = field(default_factory=dict)
    retry_count: int = 0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    id: Optional[ObjectId | str] = None

    def to_bson(self) -> JobRunDocument:
        doc: JobRunDocument = {
            "job_name": self.job_name,
            "status": self.status.value,
            "arguments": self.arguments,
            "retry_count": self.retry_count,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            doc["_id"] = self.id if isinstance(self.id, ObjectId) else ObjectId(self.id)
        return doc

    @classmethod
    def from_bson(cls, bson_data: StoredDocument) -> "JobRunModel":
        return cls(
            id=bson_data.get("_id"),
            job_name=bson_data.get("job_name", ""),
            status=JobRunStatus(bson_data["status"]),
            arguments=bson_data.get("arguments") or {},
            retry_count=bson_data.get("retry_count", 0),
            started_at=bson_data.get("started_at"),
            ended_at=bson_data.get("ended_at"),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "job_run"
