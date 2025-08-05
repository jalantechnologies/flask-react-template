from flask import Blueprint

from modules.comment.rest_api.comment_router import CommentRouter


def create_comment_blueprint() -> Blueprint:
    comment_blueprint = Blueprint("comment", __name__)
    CommentRouter.create_route(blueprint=comment_blueprint)
    return comment_blueprint 