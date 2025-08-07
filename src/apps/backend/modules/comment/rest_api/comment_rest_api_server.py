from flask import Blueprint

from modules.comment.rest_api.comment_router import CommentRouter


class CommentRestApiServer:
    @staticmethod
    def create() -> Blueprint:
        bp = Blueprint("comment", __name__)
        return CommentRouter.create_route(blueprint=bp)
