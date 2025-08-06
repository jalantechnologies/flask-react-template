from dataclasses import asdict
from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.comment.comment_service import CommentService
from modules.comment.types import (
    CreateCommentParams,
    UpdateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
)


class CommentView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str, task_id: str) -> ResponseReturnValue:
        """Create a new comment for a task"""
        request_data = request.get_json()
        if request_data is None or not request_data.get("content"):
            return jsonify({"error": "Content is required"}), 400

        params = CreateCommentParams(
            task_id=task_id,
            account_id=account_id,
            content=request_data["content"],
        )
        created_comment = CommentService.create_comment(params)
        return jsonify(asdict(created_comment)), 201

    @access_auth_middleware
    def get(self, account_id: str, task_id: str, comment_id: str = None) -> ResponseReturnValue:
        """Get single comment (by id)"""
        if comment_id:
            params = GetCommentParams(
                task_id=task_id,
                comment_id=comment_id,
                account_id=account_id,
            )
            comment = CommentService.get_comment(params)
            return jsonify(asdict(comment)), 200
        else:
            comments = CommentService.get_comments_by_task_id(task_id)
            return [comment.__dict__ for comment in comments], 200
    @access_auth_middleware
    def patch(self, account_id: str, task_id: str, comment_id: str) -> ResponseReturnValue:
        """Update a comment"""
        request_data = request.get_json()
        if request_data is None or not request_data.get("content"):
            return jsonify({"error": "Content is required"}), 400

        params = UpdateCommentParams(
            task_id=task_id,
            comment_id=comment_id,
            account_id=account_id,
            content=request_data["content"],
        )
        updated_comment = CommentService.update_comment(params)
        return jsonify(asdict(updated_comment)), 200

    @access_auth_middleware
    def delete(self, account_id: str, task_id: str, comment_id: str) -> ResponseReturnValue:
        """Delete a comment"""
        params = DeleteCommentParams(
            task_id=task_id,
            comment_id=comment_id,
            account_id=account_id,
        )
        result = CommentService.delete_comment(params)
        return jsonify(asdict(result)), 200
