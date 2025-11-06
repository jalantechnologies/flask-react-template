from flask import Blueprint
from modules.comment.rest_api.comment_router import CommentRouter

class CommentRestApiServer:
    @staticmethod
    def create() -> Blueprint:
        # Main blueprint for all comment APIs with /api prefix
        blueprint = Blueprint("comment_rest_api", __name__, url_prefix="/api")

        # Register comment routes under this blueprint
        comments_blueprint = CommentRouter.create()
        blueprint.register_blueprint(comments_blueprint)

        return blueprint