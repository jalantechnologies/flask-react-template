from datetime import datetime

from bson.objectid import ObjectId
from pymongo import ReturnDocument

from modules.comment.errors import CommentNotFound
from modules.comment.internal.comment_reader import CommentReader
from modules.comment.internal.comment_util import CommentUtil
from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import (
    Comment,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    UpdateCommentParams,
)


class CommentWriter:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        comment_bson = CommentModel(account_id=params.account_id, text=params.text, task_id=params.task_id).to_bson()

        query = CommentRepository.collection().insert_one(comment_bson)
        created_task_bson = CommentRepository.collection().find_one({"_id": query.inserted_id})

        return CommentUtil.convert_comment_bson_to_comment(created_task_bson)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        updated_comment_bson = CommentRepository.collection().find_one_and_update(
            {"_id": ObjectId(params.comment_id), "account_id": params.account_id, "task_id": params.task_id},
            {"$set": {"text": params.text, "updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER,
        )

        if updated_comment_bson is None:
            raise CommentNotFound(task_id=params.task_id)

        return CommentUtil.convert_comment_bson_to_comment(updated_comment_bson)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> None:
        comment = CommentReader.get_comment_by_id(
            params=GetCommentParams(account_id=params.account_id, task_id=params.task_id, comment_id=params.comment_id)
        )
        updated_task_bson = CommentRepository.collection().delete_one({"_id": ObjectId(comment.id)})

        if updated_task_bson is None:
            raise CommentNotFound(task_id=params.task_id)

        return None
