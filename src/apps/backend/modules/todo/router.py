# src/apps/backend/modules/todo/router.py

from flask import Blueprint

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.todo.api import create_todo, delete_todo, list_todos, update_todo

todo_bp = Blueprint("todo", __name__, url_prefix="/api/todos")


todo_bp.route("", methods=["POST"])(access_auth_middleware(create_todo))
todo_bp.route("", methods=["GET"])(access_auth_middleware(list_todos))
todo_bp.route("/<todo_id>", methods=["PUT"])(access_auth_middleware(update_todo))
todo_bp.route("/<todo_id>", methods=["DELETE"])(access_auth_middleware(delete_todo))
