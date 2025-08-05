from modules.application.common.types import PaginationResult
from modules.comment.errors import CommentNotFoundError
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import Comment, GetCommentParams, GetPaginatedCommentsParams
from modules.task.internal.task_reader import TaskReader
from modules.task.types import GetTaskParams


class CommentReader:
    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        comment_model = CommentRepository.get_comment(comment_id=params.comment_id)

        if comment_model is None:
            raise CommentNotFoundError(f"Comment with id {params.comment_id} not found")

        return Comment(
            id=str(comment_model.id),
            task_id=comment_model.task_id,
            account_id=comment_model.account_id,
            content=comment_model.content,
            created_at=comment_model.created_at,
            updated_at=comment_model.updated_at,
        )

    @staticmethod
    def get_paginated_comments(*, params: GetPaginatedCommentsParams) -> PaginationResult[Comment]:
        # Verify task exists
        task_params = GetTaskParams(task_id=params.task_id, account_id="")  # We don't need account_id for this check
        try:
            TaskReader.get_task(params=task_params)
        except Exception:
            raise CommentNotFoundError(f"Task with id {params.task_id} not found")

        offset = (params.pagination_params.page - 1) * params.pagination_params.size
        comment_models = CommentRepository.get_comments_by_task_id(
            task_id=params.task_id,
            skip=offset,
            limit=params.pagination_params.size
        )

        total_count = CommentRepository.count_comments_by_task_id(task_id=params.task_id)

        comments = [
            Comment(
                id=str(comment_model.id),
                task_id=comment_model.task_id,
                account_id=comment_model.account_id,
                content=comment_model.content,
                created_at=comment_model.created_at,
                updated_at=comment_model.updated_at,
            )
            for comment_model in comment_models
        ]

        return PaginationResult(
            items=comments,
            total_count=total_count,
            page=params.pagination_params.page,
            size=params.pagination_params.size,
        ) 