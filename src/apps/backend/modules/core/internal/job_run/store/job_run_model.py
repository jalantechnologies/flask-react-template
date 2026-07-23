from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from bson import ObjectId

from modules.core.base_model import BaseModel
from modules.core.common.types import JobArguments, JobRunStatus


@dataclass
class JobRunModel(BaseModel):
    job_name: str
    status: JobRunStatus
    arguments: JobArguments = field(default_factory=dict)
    retry_count: int = 0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    id: Optional[ObjectId | str] = None

    @classmethod
    def from_bson(cls, bson_data: dict[str, Any]) -> "JobRunModel":
        return cls(
            id=bson_data.get("_id"),
            job_name=bson_data["job_name"],
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
