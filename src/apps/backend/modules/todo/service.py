from bson import ObjectId

from modules.todo.models import TodoCreate, TodoUpdate
from modules.todo.todo_repository import TodoRepository


def create_todo_for_user(user_id: str, data: TodoCreate) -> dict:
    todo_doc = {
        "user_id": user_id,
        "title": data.title,
        "description": data.description,
        "type": data.type,
        "due_date": data.due_date,
        "status": "To Do",
    }
    inserted = TodoRepository.insert(todo_doc)
    inserted["_id"] = str(inserted["_id"])
    return inserted


def serialize_todo(todo: dict) -> dict:
    todo["_id"] = str(todo["_id"])
    return todo


def list_todos_for_user(user_id: str, status: str = None, overdue: bool = False) -> list[dict]:
    todos = TodoRepository.find_by_user(user_id)

    # You can add status and overdue filtering here if needed
    serialized = [serialize_todo(todo) for todo in todos]
    return serialized


def update_todo_item(todo_id: str, data: TodoUpdate) -> None:
    try:
        _id = ObjectId(todo_id)
    except bson_errors.InvalidId:
        raise AppError("Invalid TODO ID format", http_code=400)

    print(f"🔧 Attempting to update todo with _id: {_id}")

    result = TodoRepository.collection().update_one({"_id": _id}, {"$set": data.dict(exclude_unset=True)})

    print(f"🧪 Matched: {result.matched_count}, Modified: {result.modified_count}")

    if result.matched_count == 0:
        raise AppError("Todo not found", http_code=404)


def delete_todo_item(todo_id: str) -> None:
    TodoRepository.delete_by_id(todo_id)
