from flask import Blueprint
from .comment_view import add_comment, update_comment, delete_comment, list_comments

bp = Blueprint("comments", __name__)

bp.add_url_rule("/api/comments", view_func=add_comment, methods=["POST"])
bp.add_url_rule("/api/comments/<int:comment_id>", view_func=update_comment, methods=["PUT"])
bp.add_url_rule("/api/comments/<int:comment_id>", view_func=delete_comment, methods=["DELETE"])
bp.add_url_rule("/api/tasks/<int:task_id>/comments", view_func=list_comments, methods=["GET"])
