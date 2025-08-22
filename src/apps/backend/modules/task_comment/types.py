from datetime import datetime
from typing import Optional, List, Union   
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Import from other modules
from modules.application.common.types import PaginationParams


class TaskComment(BaseModel):
    """Task comment domain model"""
    model_config = ConfigDict(frozen=True)
    
    id: str
    task_id: str
    account_id: str
    content: str
    created_at: datetime
    updated_at: datetime


class CreateTaskCommentParams(BaseModel):
    """Parameters for creating a task comment"""
    task_id: str
    account_id: str
    content: str = Field(..., min_length=1, max_length=200)
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Comment content cannot be empty')
        return v


class UpdateTaskCommentParams(BaseModel):
    """Parameters for updating a task comment"""
    comment_id: str
    task_id: str
    account_id: str  # for authorization check
    content: str = Field(..., min_length=1, max_length=200)
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Comment content cannot be empty')
        return v


class DeleteTaskCommentParams(BaseModel):
    """Parameters for deleting a task comment"""
    comment_id: str
    task_id: str
    account_id: str  # for authorization check


class GetTaskCommentsParams(BaseModel):
    """Parameters for retrieving task comments"""
    task_id: str
    account_id: Optional[str] = None  # optional: to check if user can see private comments
    pagination_params: Optional[PaginationParams] = None


class TaskCommentListResponse(BaseModel):
    """Response for task comment list"""
    comments: List[TaskComment]
    task_id: str
    total_count: int
    page: int
    limit: int
    has_more: bool


class TaskCommentResponse(BaseModel):
    """Single task comment response"""
    comment: TaskComment
    
    
class TaskCommentDeletionResult(BaseModel):
    """Result of comment deletion operation"""
    comment_id: str
    deleted_at: datetime
    success: bool
    message: str = "Comment deleted successfully"


# Error code constants using Python Enum for better type safety
from enum import Enum

class TaskCommentErrorCode(str, Enum):
    """Error codes for task comment operations"""
    COMMENT_NOT_FOUND = "TASK_COMMENT_ERR_01"
    UNAUTHORIZED_EDIT = "TASK_COMMENT_ERR_02"
    UNAUTHORIZED_DELETE = "TASK_COMMENT_ERR_03"
    TASK_NOT_FOUND = "TASK_COMMENT_ERR_04"
    INVALID_CONTENT = "TASK_COMMENT_ERR_05"
    COMMENT_LOCKED = "TASK_COMMENT_ERR_06"
   
    
    
# Request/Response models for REST API
class CreateTaskCommentRequest(BaseModel):
    """HTTP request body for creating a comment"""
    content: str
    
    
class UpdateTaskCommentRequest(BaseModel):
    """HTTP request body for updating a comment"""
    content: str
    
    
class TaskCommentFilters(BaseModel):
    """Filters for querying task comments"""
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    author_id: Optional[str] = None
    search_text: Optional[str] = None