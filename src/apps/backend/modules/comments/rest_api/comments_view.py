from flask import jsonify, request
from flask.views import MethodView

from modules.comments.comments_service import CommentService
from modules.comments.types import CreateCommentParams, DeleteCommentParams, GetCommentsParams, UpdateCommentParams


class CommentView(MethodView):

    def post(self, account_id, task_id):
        data = request.json

        if not data or "text" not in data:
            return jsonify({"error": "Text is required"}), 400

        if not data.get("text", "").strip():
            return jsonify({"error": "Text cannot be empty"}), 400

        params = CreateCommentParams(account_id=account_id, task_id=task_id, text=data["text"])

        comment = CommentService.create_comment(params=params)
        return jsonify(comment.to_dict()), 201

    def get(self, account_id, task_id):
        """Get all comments for a task"""
        params = GetCommentsParams(account_id=account_id, task_id=task_id)

        comments = CommentService.get_comments(params=params)
        return jsonify([c.to_dict() for c in comments]), 200


class CommentViewById(MethodView):

    def put(self, account_id, task_id, comment_id):
        data = request.json

        # Validation
        if not data or "text" not in data:
            return jsonify({"error": "Text is required"}), 400

        if not data.get("text", "").strip():
            return jsonify({"error": "Text cannot be empty"}), 400

        params = UpdateCommentParams(account_id=account_id, task_id=task_id, comment_id=comment_id, text=data["text"])

        comment = CommentService.update_comment(params=params)
        if comment:
            return jsonify(comment.to_dict()), 200
        return jsonify({"error": "Comment not found"}), 404

    def delete(self, account_id, task_id, comment_id):
        params = DeleteCommentParams(account_id=account_id, task_id=task_id, comment_id=comment_id)

        result = CommentService.delete_comment(params=params)
        if result.success:
            return jsonify({"status": "deleted"}), 200
        return jsonify({"error": "Comment not found"}), 404
