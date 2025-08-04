from flask import Blueprint
from modules.task.comments.rest_api.comments_router import CommentRouter

class CommentsRestApiServer:
    @staticmethod
    def create() -> Blueprint:
        comments_api_blueprint = Blueprint("comments", __name__)
        return CommentRouter.create_route(blueprint=comments_api_blueprint)