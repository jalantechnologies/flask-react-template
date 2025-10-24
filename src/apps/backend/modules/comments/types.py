from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateCommentParams:
    account_id: str
    task_id: str
    text: str


@dataclass
class GetCommentsParams:
    account_id: str
    task_id: str


@dataclass
class UpdateCommentParams:
    account_id: str
    task_id: str
    comment_id: str
    text: str


@dataclass
class DeleteCommentParams:
    account_id: str
    task_id: str
    comment_id: str


@dataclass
class Comment:
    id: str
    account_id: str
    task_id: str
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "task_id": self.task_id,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class CommentDeletionResult:
    success: bool
    comment_id: str


class CommentErrorCode:
    BAD_REQUEST = "COMMENT_BAD_REQUEST"
    NOT_FOUND = "COMMENT_NOT_FOUND"
    UNAUTHORIZED = "COMMENT_UNAUTHORIZED"
