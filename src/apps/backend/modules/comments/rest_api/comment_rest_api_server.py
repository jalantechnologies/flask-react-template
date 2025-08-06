from modules.comments.rest_api.comment_router import comment_blueprint

class CommentRestApiServer:
    @staticmethod
    def create():
        return comment_blueprint