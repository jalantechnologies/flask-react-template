from flask import jsonify, request
from flask.views import MethodView

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.comments.comments_service import CommentsService
from modules.comments.types import CreateCommentParams, DeleteCommentParams, UpdateCommentParams


class CommentsView(MethodView):

    @access_auth_middleware
    def get(self, task_id: str, comment_id: str = None):
        print("🟢 Reached GET /comments")

        if comment_id:
            comment = CommentsService.get_comment_by_id(comment_id)
            if not comment:
                return jsonify({"error": "Comment not found"}), 404
            return jsonify(comment), 200
        else:
            comments = CommentsService.get_comments_by_task_id(task_id)
            return jsonify(comments), 200

    @access_auth_middleware
    def post(self, task_id: str):
        data = request.get_json()

        if not data or not data.get("account_id") or not data.get("content"):
            return jsonify({"error": "account_id and content are required"}), 400

        params = CreateCommentParams(task_id=task_id, account_id=data["account_id"], content=data["content"])
        comment = CommentsService.create_comment(params)
        return jsonify(comment), 201

    @access_auth_middleware
    def patch(self, task_id: str, comment_id: str):
        data = request.get_json()

        if not data or not data.get("content"):
            return jsonify({"error": "content is required"}), 400

        params = UpdateCommentParams(comment_id=comment_id, content=data["content"])
        comment = CommentsService.update_comment(params)
        return jsonify(comment), 200

    @access_auth_middleware
    def delete(self, task_id: str, comment_id: str):
        params = DeleteCommentParams(comment_id=comment_id)
        CommentsService.delete_comment(params)
        return "", 204
