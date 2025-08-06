from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Comment:
    id:str
    task_id:str
    author:str
    content:str
    created_at:datetime
    
@dataclass(frozen=True)
class CreatedCommentParams:
    task_id:str
    author:str
    content:str
    
@dataclass(frozen=True)
class UpdateCommentParams:
    comment_id : str
    content:str
    
@dataclass(frozen=True)
class DeleteCommentParams:
    comment_id: str
    
@dataclass(frozen = True)
class CommentErrorCode:
    NOT_FOUND:str = "COMMENT_ERR_01"
    BAD_REQUEST:str="COMMENT_ERR_02"