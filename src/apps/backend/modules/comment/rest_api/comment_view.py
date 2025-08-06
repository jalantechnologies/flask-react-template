from dataclasses import asdict

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
    GetPaginatedCommentsParams,
    UpdateCommentParams,
)


class CommentView(MethodView):
    @access_auth_middleware
    def post(self, task_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError("Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError("Content is required")

        create_comment_params = CreateCommentParams(task_id=task_id, content=request_data["content"])

        created_comment = CommentService.create_comment(params=create_comment_params)
        comment_dict = asdict(created_comment)

        return jsonify(comment_dict), 201

    @access_auth_middleware
    def get(self, task_id: str) -> ResponseReturnValue:
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
        comments_params = GetPaginatedCommentsParams(task_id=task_id, pagination_params=pagination_params)

        pagination_result = CommentService.get_paginated_comments(params=comments_params)

        response_data = asdict(pagination_result)

        return jsonify(response_data), 200


class CommentByIdView(MethodView):
    @access_auth_middleware
    def put(self, comment_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError("Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError("Content is required")

        # Get the task_id from the comment to validate ownership
        comment = CommentService.get_comment(params=GetCommentParams(task_id="", comment_id=comment_id))

        update_comment_params = UpdateCommentParams(
            task_id=comment.task_id, comment_id=comment_id, content=request_data["content"]
        )

        updated_comment = CommentService.update_comment(params=update_comment_params)
        comment_dict = asdict(updated_comment)

        return jsonify(comment_dict), 200

    @access_auth_middleware
    def delete(self, comment_id: str) -> ResponseReturnValue:
        # Get the task_id from the comment to validate ownership
        comment = CommentService.get_comment(params=GetCommentParams(task_id="", comment_id=comment_id))

        delete_params = DeleteCommentParams(task_id=comment.task_id, comment_id=comment_id)

        CommentService.delete_comment(params=delete_params)

        return "", 204
