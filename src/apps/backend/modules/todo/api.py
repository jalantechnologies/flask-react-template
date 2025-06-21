# src/apps/backend/modules/todo/api.py

from flask import jsonify, request

from modules.todo.models import TodoCreate, TodoUpdate
from modules.todo.service import create_todo_for_user, delete_todo_item, list_todos_for_user, update_todo_item


def serialize_todo(todo_doc):
    todo_doc["id"] = str(todo_doc["_id"])
    del todo_doc["_id"]
    return todo_doc


def create_todo():
    data = TodoCreate(**request.json)
    user_id = request.account_id
    todo = create_todo_for_user(user_id, data)
    return jsonify(todo), 201


def list_todos():
    status = request.args.get("status")
    overdue = request.args.get("overdue") == "true"

    user_id = request.account_id  # <- the key fix
    todos = list_todos_for_user(user_id, status, overdue)
    return jsonify(todos), 200


def update_todo(todo_id):
    try:
        update_todo_item(todo_id, TodoUpdate(**request.json))
        return "", 204  # ✅ success, no content
    except AppError as e:
        return jsonify({"error": e.message}), e.http_code
    except Exception:
        import traceback

        print("Error updating todo:", traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500


def delete_todo(todo_id):
    delete_todo_item(todo_id)
    return "", 204
