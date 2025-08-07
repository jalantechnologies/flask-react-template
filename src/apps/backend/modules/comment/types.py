from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Comment:
    id: str
    task_id: str
    account_id: str
    content: str
    active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CreateCommentParams:
    task_id: str
    account_id: str
    content: str


@dataclass(frozen=True)
class UpdateCommentParams:
    task_id: str
    comment_id: str
    account_id: str
    content: str


@dataclass(frozen=True)
class GetCommentParams:
    task_id: str
    comment_id: str
    account_id: str


@dataclass(frozen=True)
class DeleteCommentParams:
    task_id: str
    comment_id: str
    account_id: str


@dataclass(frozen=True)
class GetTaskCommentsParams:
    task_id: str
    account_id: str
    pagination_params: Optional[object] = None
