from dataclasses import dataclass
from datetime import datetime

# Represents a single Comment
@dataclass(frozen=True)
class Comment:
    id: str
    task_id: str
    account_id: str
    content: str

# Create Comment
@dataclass(frozen=True)
class CreateCommentParams:
    task_id: str
    account_id: str
    content: str

# Update Comment
@dataclass(frozen=True)
class UpdateCommentParams:
    task_id: str
    comment_id: str
    account_id: str
    content: str

# Delete Comment
@dataclass(frozen=True)
class DeleteCommentParams:
    task_id: str
    comment_id: str
    account_id: str

# Get Single Comment
@dataclass(frozen=True)
class GetCommentParams:
    task_id: str
    comment_id: str
    account_id: str

# Result of deletion
@dataclass(frozen=True)
class CommentDeletionResult:
    comment_id: str
    deleted_at: datetime
    success: bool
