import uuid
from datetime import datetime

from modules.comments.internal.store.comments_repository import CommentRepository
from modules.comments.types import (
    Comment,
    CommentDeletionResult,
    CreateCommentParams,
    DeleteCommentParams,
    UpdateCommentParams,
)


class CommentWriter:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        comment = Comment(
            id=str(uuid.uuid4()),
            account_id=params.account_id,
            task_id=params.task_id,
            text=params.text,
            created_at=datetime.utcnow(),
        )
        return CommentRepository.add_comment(comment)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        return CommentRepository.update_comment(
            account_id=params.account_id, task_id=params.task_id, comment_id=params.comment_id, text=params.text
        )

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        success = CommentRepository.delete_comment(
            account_id=params.account_id, task_id=params.task_id, comment_id=params.comment_id
        )
        return CommentDeletionResult(success=success, comment_id=params.comment_id)
