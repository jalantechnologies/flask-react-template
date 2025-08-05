from typing import List, Optional

from bson import ObjectId

from modules.application.database import get_database
from modules.comment.internal.store.comment_model import CommentModel


class CommentRepository:
    @staticmethod
    def create_comment(*, comment_model: CommentModel) -> CommentModel:
        database = get_database()
        collection = database[CommentModel.get_collection_name()]

        comment_dict = comment_model.__dict__.copy()
        comment_dict.pop("id", None)

        result = collection.insert_one(comment_dict)
        comment_model.id = result.inserted_id

        return comment_model

    @staticmethod
    def get_comment(*, comment_id: str) -> Optional[CommentModel]:
        database = get_database()
        collection = database[CommentModel.get_collection_name()]

        bson_data = collection.find_one({"_id": ObjectId(comment_id), "active": True})

        if bson_data is None:
            return None

        return CommentModel.from_bson(bson_data)

    @staticmethod
    def get_comments_by_task_id(*, task_id: str, skip: int = 0, limit: int = 10) -> List[CommentModel]:
        database = get_database()
        collection = database[CommentModel.get_collection_name()]

        cursor = collection.find(
            {"task_id": task_id, "active": True},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )

        return [CommentModel.from_bson(bson_data) for bson_data in cursor]

    @staticmethod
    def count_comments_by_task_id(*, task_id: str) -> int:
        database = get_database()
        collection = database[CommentModel.get_collection_name()]

        return collection.count_documents({"task_id": task_id, "active": True})

    @staticmethod
    def update_comment(*, comment_id: str, content: str) -> Optional[CommentModel]:
        database = get_database()
        collection = database[CommentModel.get_collection_name()]

        from datetime import datetime

        result = collection.update_one(
            {"_id": ObjectId(comment_id), "active": True},
            {"$set": {"content": content, "updated_at": datetime.now()}}
        )

        if result.modified_count == 0:
            return None

        bson_data = collection.find_one({"_id": ObjectId(comment_id)})
        return CommentModel.from_bson(bson_data)

    @staticmethod
    def delete_comment(*, comment_id: str) -> bool:
        database = get_database()
        collection = database[CommentModel.get_collection_name()]

        from datetime import datetime

        result = collection.update_one(
            {"_id": ObjectId(comment_id), "active": True},
            {"$set": {"active": False, "updated_at": datetime.now()}}
        )

        return result.modified_count > 0 