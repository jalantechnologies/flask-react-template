from bson.objectid import ObjectId

from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.internal.comment_util import CommentUtil
from modules.comment.types import GetCommentsParams, Comment


class CommentReader:
    @staticmethod
    def get_comments_by_task_id(*, params: GetCommentsParams) -> list[Comment]:
        filter_query = {"account_id": params.account_id, "task_id": params.task_id, "active": True}
        
        cursor = CommentRepository.collection().find(filter_query).sort("created_at", 1) # Oldest first usually for comments
        
        comments_bson = list(cursor)
        return [CommentUtil.convert_comment_bson_to_comment(comment_bson) for comment_bson in comments_bson]
