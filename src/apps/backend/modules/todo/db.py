# src/apps/backend/modules/todo/db.py

from datetime import datetime

from bson import ObjectId
from flask import current_app

from modules.todo.models import TodoCreate, TodoUpdate


def get_todo_collection():
    return current_app.mongo_client["app"]["todos"]


def create_todo(user_id: str, data: TodoCreate):
    todo = data.dict()
    todo.update({"user_id": user_id, "status": "To Do", "created_at": datetime.utcnow()})
    result = get_todo_collection().insert_one(todo)
    todo["id"] = str(result.inserted_id)
    return todo


def get_user_todos(user_id: str):
    todos = get_todo_collection().find({"user_id": user_id})
    return [{**todo, "id": str(todo["_id"])} for todo in todos]


def get_todo_by_id(todo_id: str):
    return get_todo_collection().find_one({"_id": ObjectId(todo_id)})


def update_todo(todo_id: str, update_data: TodoUpdate):
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    get_todo_collection().update_one({"_id": ObjectId(todo_id)}, {"$set": update_dict})


def delete_todo(todo_id: str):
    get_todo_collection().delete_one({"_id": ObjectId(todo_id)})
