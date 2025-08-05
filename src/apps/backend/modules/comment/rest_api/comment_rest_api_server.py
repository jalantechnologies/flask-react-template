from flask import Blueprint

from modules.comment.rest_api.comment_router import CommentRouter


class CommentRestApiServer:
    @staticmethod
    def create_blueprint() -> Blueprint:
        blueprint = Blueprint("comment", __name__)
        CommentRouter.create_route(blueprint=blueprint)
        return blueprint 