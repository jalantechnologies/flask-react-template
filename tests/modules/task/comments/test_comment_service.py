from datetime import datetime
from modules.application.common.types import PaginationParams
from modules.task.comments.comment_service import CommentService
from modules.task.comments.errors import CommentNotFoundError, CommentTaskNotFoundError
from modules.task.comments.types import (
    CreateCommentParams,
    GetCommentParams,
    CommentErrorCode
)
from tests.modules.task.comments.base_test_comment import BaseTestComment


class TestCommentService(BaseTestComment):
    """
    Test suite for CommentService business logic validation.
    
    """

    def setUp(self) -> None:
        """
        Set up test data for each test method.
        """
        super().setUp()
        # create test account and task for comment operations
        self.account, self.token = self.create_account_and_get_token()
        self.task = self.create_test_task(account_id=self.account.id)

    # Create comment test

    def test_create_comment_success(self) -> None:
        """
        Test successful comment creation with valid parent task

        Business rules validated:
        - parent task must exists and belong to account
        - comment content must be provided
        - timetamps are auto-generated
        - comment object is properly populated
        """

        params = CreateCommentParams(
            account_id=self.account.id,
            task_id=self.task.id,
            content=self.DEFAULT_COMMENT_CONTENT
        )

        comment = CommentService.create_comment(params=params)

        assert comment.account_id == self.account.id
        assert comment.task_id == self.task.id
        assert comment.content == self.DEFAULT_COMMENT_CONTENT
        assert comment.id is not None
        assert comment.created_at is not None
        assert comment.updated_at is not None
        assert isinstance(comment.created_at, datetime)

    def test_create_comment_missing_parent_task(self) -> None:
        """
        Test comment creation fails when parent task doesn't exist.
        Business rule: Comment require valid parent task
        - service validates task existence before creation
        - proper error code returned for missing task
        """

        non_existent_task_id = "801e1f77bcf86cd799431899"
        
        with self.assertRaises(CommentTaskNotFoundError) as context:
            CommentService.create_comment(
                params=CreateCommentParams(
                    account_id=self.account.id,
                    task_id=non_existent_task_id,
                    content=self.DEFAULT_COMMENT_CONTENT
                )
            )
        
        assert context.exception.code == CommentErrorCode.TASK_NOT_FOUND

    def test_create_comment_cross_account_task(self) -> None:
        """
        Test comment creation fails for cross-account task access.
        
        Business logic:
        - Users cannot create comments on other users' tasks
       
        """
        # Create task under different account
        other_account, _ = self.create_account_and_get_token()
        other_task = self.create_test_task(account_id=other_account.id)

        params = CreateCommentParams(
            account_id=self.account.id,  # Different account than task owner
            task_id=other_task.id,
            content=self.DEFAULT_COMMENT_CONTENT
        )

        with self.assertRaises(CommentTaskNotFoundError) as context:
            CommentService.create_comment(params=params)

        assert context.exception.code == CommentErrorCode.TASK_NOT_FOUND

    # Get comment tests
    def test_get_comment_success(self) -> None:
        """
        Test successful comment retrieval with valid comment ID
        validation:
        - comment exists and belongs to account
        - all fields are populated
        - parent task validation occurs
        - returned object matches created comment
        """

        created_comment = self.create_test_comment(
            account_id=self.account.id,
            task_id=self.task.id
        )

        params = GetCommentParams(
            account_id=self.account.id,
            task_id=self.task.id,
            comment_id=created_comment.id
        )

        retrieved_comment = CommentService.get_comment(params=params)

        assert retrieved_comment.id == created_comment.id
        assert retrieved_comment.account_id == self.account.id
        assert retrieved_comment.task_id == self.task.id
        assert retrieved_comment.content == self.DEFAULT_COMMENT_CONTENT
