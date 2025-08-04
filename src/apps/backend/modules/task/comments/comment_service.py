from modules.task.types import GetTaskParams
from modules.application.common.types import PaginationResult
from modules.task.comments.errors import CommentTaskNotFoundError
from modules.task.comments.internal.comment_reader import CommentReader
from modules.task.comments.internal.comment_writer import CommentWriter
from modules.task.comments.types import (
    CreateCommentParams,
    UpdateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    Comment,
    CommentDeletionResult,
)
from modules.task.internal.task_reader import TaskReader
from modules.task.internal.task_writer import TaskWriter
from modules.task.errors import TaskNotFoundError

class CommentService:
    """
    Business logic for comment operations

    Responsibility: Coordinate coment opeations with business rule enforcement
    - Parent task validation for all comment operations
    - Business rule enforcement and validation
    - Error handling and consistent response
    - Coordination between comment and task data layers

    Static service class
    - No state required, pure business logic
    - Easy to test and mock dependencies
    - Consistent with TaskService pattern
    - Clear separation of concerns

    Business logic:
    - task existence validaiton before coment operations
    - security enforcement through task ownership
    - consistent error handling across operations
    - data validation and transformation

    """

    @staticmethod
    def _validate_task_exists(*, account_id: str, task_id: str) -> None:
        """
        Validate that parent task exists and belongs to account.
        """

        try:
            TaskReader.get_task(
                params=GetTaskParams(
                    account_id=account_id,
                    task_id=task_id
                )
            )
        except TaskNotFoundError:
            raise CommentTaskNotFoundError(task_id=task_id)
        
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        """
        Create a new comment with parent task validation.
        """

        CommentService._validate_task_exists(
            account_id=params.account_id,
            task_id=params.task_id
        )

        # Delegate to CommentWriter for data persistence
        created_comment = CommentWriter.create_comment(
            params=params
        )
        
        return created_comment
    
    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        """
        Retrieve a specific comment with parent task validation.
        """

        CommentService._validate_task_exists(
            account_id=params.account_id,
            task_id=params.task_id
        )

        # Delegate to CommentReader for data retrieval
        return CommentReader.get_comment(
            params=params
        )
    
    @staticmethod
    def get_paginated_comments(*, params: GetPaginatedCommentsParams) -> PaginationResult[Comment]:
        """
        Retrieve paginated list of comments for a specific task.
        """

        CommentService._validate_task_exists(
            account_id=params.account_id,
            task_id=params.task_id
        )
        
        return CommentReader.get_paginated_comments(params=params)
    
    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        """
        Update comment content with parent task validation.
        """

        CommentService._validate_task_exists(
            account_id=params.account_id,
            task_id=params.task_id
        )

        # Delegate to CommentWriter for data persistence
        return CommentWriter.update_comment(params=params)
    
    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        """
        Delete comment with parent task validation. 
        """

        CommentService._validate_task_exists(
            account_id=params.account_id,
            task_id=params.task_id
        )

        return CommentWriter.delete_comment(params=params)