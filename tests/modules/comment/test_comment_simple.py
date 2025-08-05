import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src/apps/backend'))

from modules.comment.types import Comment, CreateCommentParams, GetCommentParams
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentNotFoundError


def test_comment_types():
    """Test that comment types can be created"""
    comment = Comment(
        id="test_id",
        task_id="task_id",
        account_id="account_id",
        content="test content",
        created_at=None,
        updated_at=None
    )
    
    assert comment.id == "test_id"
    assert comment.task_id == "task_id"
    assert comment.account_id == "account_id"
    assert comment.content == "test content"


def test_create_comment_params():
    """Test that CreateCommentParams can be created"""
    params = CreateCommentParams(
        task_id="task_id",
        account_id="account_id",
        content="test content"
    )
    
    assert params.task_id == "task_id"
    assert params.account_id == "account_id"
    assert params.content == "test content"


def test_get_comment_params():
    """Test that GetCommentParams can be created"""
    params = GetCommentParams(
        task_id="task_id",
        comment_id="comment_id"
    )
    
    assert params.task_id == "task_id"
    assert params.comment_id == "comment_id"


def test_comment_error_codes():
    """Test that comment error codes are defined"""
    from modules.comment.types import CommentErrorCode
    
    assert CommentErrorCode.NOT_FOUND == "COMMENT_ERR_01"
    assert CommentErrorCode.BAD_REQUEST == "COMMENT_ERR_02"
    assert CommentErrorCode.TASK_NOT_FOUND == "COMMENT_ERR_03"


def test_comment_errors():
    """Test that comment errors can be created"""
    from modules.comment.errors import CommentNotFoundError, CommentBadRequestError, TaskNotFoundError
    
    # Test CommentNotFoundError
    error = CommentNotFoundError("Comment not found")
    assert str(error) == "Comment not found"
    assert error.error_code == "COMMENT_ERR_01"
    
    # Test CommentBadRequestError
    error = CommentBadRequestError("Bad request")
    assert str(error) == "Bad request"
    assert error.error_code == "COMMENT_ERR_02"
    
    # Test TaskNotFoundError
    error = TaskNotFoundError("Task not found")
    assert str(error) == "Task not found"
    assert error.error_code == "COMMENT_ERR_03"


if __name__ == "__main__":
    print("Running simple comment tests...")
    test_comment_types()
    test_create_comment_params()
    test_get_comment_params()
    test_comment_error_codes()
    test_comment_errors()
    print("All simple tests passed!") 