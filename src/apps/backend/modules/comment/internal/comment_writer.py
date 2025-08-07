from datetime import datetime, timezone

from bson import ObjectId

from modules.comment.errors import CommentForbiddenError, CommentNotFoundError
from modules.comment.internal.comment_util import CommentUtil
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import Comment, CreateCommentParams, DeleteCommentParams, UpdateCommentParams


class CommentWriter:
    def __init__(self):
        self.repository = CommentRepository()

    def create_comment(self, params: CreateCommentParams) -> Comment:
        comment_data = {
            "task_id": params.task_id,
            "account_id": params.account_id,
            "content": params.content,
            "active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = self.repository.collection().insert_one(comment_data)
        comment_data["_id"] = result.inserted_id

        return CommentUtil.convert_comment_bson_to_comment(comment_data)

    def update_comment(self, params: UpdateCommentParams) -> Comment:
        comment_id = ObjectId(params.comment_id)

        existing_comment = self.repository.collection().find_one(
            {"_id": comment_id, "task_id": params.task_id, "active": True}
        )

        if not existing_comment:
            raise CommentNotFoundError()

        if existing_comment["account_id"] != params.account_id:
            raise CommentForbiddenError()

        update_data = {"content": params.content, "updated_at": datetime.now(timezone.utc)}

        updated_comment = self.repository.collection().find_one_and_update(
            {"_id": comment_id},
            {"$set": update_data},
            return_document=True,  # may need to use ReturnDocument.AFTER if not returning correctly
        )

        return CommentUtil.convert_comment_bson_to_comment(updated_comment)

    def delete_comment(self, params: DeleteCommentParams) -> None:
        comment_id = ObjectId(params.comment_id)

        existing_comment = self.repository.collection().find_one(
            {"_id": comment_id, "task_id": params.task_id, "active": True}
        )

        if not existing_comment:
            raise CommentNotFoundError()

        if existing_comment["account_id"] != params.account_id:
            raise CommentForbiddenError()

        self.repository.collection().update_one(
            {"_id": comment_id}, {"$set": {"active": False, "updated_at": datetime.now(timezone.utc)}}
        )
