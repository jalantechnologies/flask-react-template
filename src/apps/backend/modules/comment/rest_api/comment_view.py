from dataclasses import asdict
from typing import Optional

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.application.common.constants import DEFAULT_PAGINATION_PARAMS
from modules.application.common.types import PaginationParams
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentBadRequestError
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentParams,
    UpdateCommentParams,
)


class CommentView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError("Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError("Content is required")

        if not request_data.get("task_id"):
            raise CommentBadRequestError("Task ID is required")

        create_params = CreateCommentParams(
            account_id=account_id, 
            task_id=request_data["task_id"], 
            content=request_data["content"]
        )

        created_comment = CommentService.create_comment(params=create_params)
        return jsonify(asdict(created_comment)), 201

    @access_auth_middleware
    def get(self, account_id: str, comment_id: Optional[str] = None) -> ResponseReturnValue:
        task_id = request.args.get("task_id")
        if not task_id:
            raise CommentBadRequestError("Task ID is required")

        if comment_id:
            params = GetCommentParams(account_id=account_id, task_id=task_id, comment_id=comment_id)
            comment = CommentService.get_comment(params=params)
            return jsonify(asdict(comment)), 200

        page = request.args.get("page", type=int)
        size = request.args.get("size", type=int)

        if page is not None and page < 1:
            raise CommentBadRequestError("Page must be greater than 0")

        if size is not None and size < 1:
            raise CommentBadRequestError("Size must be greater than 0")

        if page is None:
            page = DEFAULT_PAGINATION_PARAMS.page
        if size is None:
            size = DEFAULT_PAGINATION_PARAMS.size

        pagination_params = PaginationParams(page=page, size=size, offset=0)
        get_params = GetPaginatedCommentParams(
            account_id=account_id, task_id=task_id, pagination_params=pagination_params
        )

        pagination_result = CommentService.get_paginated_comments(params=get_params)
        return jsonify(asdict(pagination_result)), 200

    @access_auth_middleware
    def patch(self, account_id: str, comment_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError("Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError("Content is required")

        if not request_data.get("task_id"):
            raise CommentBadRequestError("Task ID is required")

        update_params = UpdateCommentParams(
            account_id=account_id, 
            task_id=request_data["task_id"], 
            comment_id=comment_id, 
            content=request_data["content"]
        )

        updated_comment = CommentService.update_comment(params=update_params)
        return jsonify(asdict(updated_comment)), 200

    @access_auth_middleware
    def delete(self, account_id: str, comment_id: str) -> ResponseReturnValue:
        task_id = request.args.get("task_id")
        if not task_id:
            raise CommentBadRequestError("Task ID is required")

        delete_params = DeleteCommentParams(account_id=account_id, task_id=task_id, comment_id=comment_id)
        CommentService.delete_comment(params=delete_params)
        return "", 204
