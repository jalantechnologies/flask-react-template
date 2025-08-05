from datetime import datetime

from modules.comment.errors import CommentNotFoundError
from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import Comment, CommentDeletionResult, CreateCommentParams, DeleteCommentParams, UpdateCommentParams
from modules.task.internal.task_reader import TaskReader
from modules.task.types import GetTaskParams


class CommentWriter:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        # Verify task exists
        task_params = GetTaskParams(task_id=params.task_id, account_id=params.account_id)
        try:
            TaskReader.get_task(params=task_params)
        except Exception:
            raise CommentNotFoundError(f"Task with id {params.task_id} not found")

        comment_model = CommentModel(
            task_id=params.task_id,
            account_id=params.account_id,
            content=params.content,
        )

        created_comment_model = CommentRepository.create_comment(comment_model=comment_model)

        return Comment(
            id=str(created_comment_model.id),
            task_id=created_comment_model.task_id,
            account_id=created_comment_model.account_id,
            content=created_comment_model.content,
            created_at=created_comment_model.created_at,
            updated_at=created_comment_model.updated_at,
        )

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        updated_comment_model = CommentRepository.update_comment(
            comment_id=params.comment_id,
            content=params.content
        )

        if updated_comment_model is None:
            raise CommentNotFoundError(f"Comment with id {params.comment_id} not found")

        return Comment(
            id=str(updated_comment_model.id),
            task_id=updated_comment_model.task_id,
            account_id=updated_comment_model.account_id,
            content=updated_comment_model.content,
            created_at=updated_comment_model.created_at,
            updated_at=updated_comment_model.updated_at,
        )

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        success = CommentRepository.delete_comment(comment_id=params.comment_id)

        if not success:
            raise CommentNotFoundError(f"Comment with id {params.comment_id} not found")

        return CommentDeletionResult(
            comment_id=params.comment_id,
            deleted_at=datetime.now(),
            success=True,
        ) 