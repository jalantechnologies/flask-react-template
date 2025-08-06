from datetime import datetime
from bson import ObjectId
from pymongo.collection import Collection
from modules.comments.domain.models import (
    Comment,
    CreatedCommentParams,
    UpdateCommentParams,
    DeleteCommentParams,
)
from modules.application.mongo.mongo_service import MongoService


class CommentService:
    def __init__(self):
        self.collection: Collection = MongoService.get_collection("comments")

    def create_comment(self, params: CreatedCommentParams) -> Comment:
        comment_data = {
            "task_id": ObjectId(params.task_id),
            "author": params.author,
            "content": params.content,
            "created_at": datetime.utcnow(),
        }
        result = self.collection.insert_one(comment_data)
        return Comment(
            id=str(result.inserted_id),
            task_id=params.task_id,
            author=params.author,
            content=params.content,
            created_at=comment_data["created_at"],
        )

    def update_comment(self, params: UpdateCommentParams) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(params.comment_id)},
            {"$set": {"content": params.content}},
        )
        return result.modified_count > 0

    def delete_comment(self, params: DeleteCommentParams) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(params.comment_id)})
        return result.deleted_count > 0

    def get_comments_by_task(self, task_id: str) -> list[Comment]:
        comments_cursor = self.collection.find({"task_id": ObjectId(task_id)}).sort("created_at", 1)
        comments = []
        for doc in comments_cursor:
            comments.append(
                Comment(
                    id=str(doc["_id"]),
                    task_id=str(doc["task_id"]),
                    author=doc["author"],
                    content=doc["content"],
                    created_at=doc["created_at"],
                )
            )
        return comments
