from typing import Any, Dict

from bson import ObjectId

from modules.application.repository import ApplicationRepository


class TodoRepository(ApplicationRepository):
    collection_name = "todos"

    @classmethod
    def insert(cls, document: Dict[str, Any]) -> Dict[str, Any]:
        result = cls.collection().insert_one(document)
        return {**document, "_id": str(result.inserted_id)}

    @classmethod
    def find_by_user(cls, user_id: str) -> list[Dict[str, Any]]:
        return list(cls.collection().find({"user_id": user_id}))

    @classmethod
    def update_status(cls, todo_id: str, status: str) -> None:
        cls.collection().update_one({"_id": todo_id}, {"$set": {"status": status}})

    @classmethod
    def delete_by_id(cls, todo_id: str) -> None:
        cls.collection().delete_one({"_id": ObjectId(todo_id)})
