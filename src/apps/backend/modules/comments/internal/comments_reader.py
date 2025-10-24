from typing import List

from modules.comments.internal.store.comments_repository import CommentRepository
from modules.comments.types import Comment, GetCommentsParams


class CommentReader:
    @staticmethod
    def get_comments(*, params: GetCommentsParams) -> List[Comment]:
        return CommentRepository.get_comments_by_task(account_id=params.account_id, task_id=params.task_id)
