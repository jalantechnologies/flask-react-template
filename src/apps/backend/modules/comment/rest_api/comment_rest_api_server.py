from modules.comment.rest_api.comment_router import bp as comment_bp

class CommentRestApiServer:
    @staticmethod
    def create():
        return comment_bp
