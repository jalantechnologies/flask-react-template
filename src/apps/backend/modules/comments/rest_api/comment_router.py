from flask import Blueprint
from modules.comments.rest_api.comment_view import CommentView

comment_blueprint = Blueprint("comments", __name__, url_prefix="/api/comments")

comment_view = CommentView.as_view("comment_view")

comment_view = CommentView.as_view("comment_view")
comment_blueprint.add_url_rule("/", view_func=comment_view, methods=["GET", "POST"])
