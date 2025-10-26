from dataclasses import asdict
from typing import Optional

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.application.common.constants import DEFAULT_PAGINATION_PARAMS
from modules.application.common.types import PaginationParams
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.comment.comment_service import CommentService
from modules.comment.types import CreateCommentParams, DeleteCommentParams, GetTaskParams, UpdateCommentParams
from modules.task.errors import TaskBadRequestError


class CommentView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str, task_id: str) -> ResponseReturnValue:
        request_data = request.get_json()
        create_task_params = CreateCommentParams(account_id=account_id, text=request_data["text"], task_id=task_id)
        created_task = CommentService.create_comment(params=create_task_params)
        task_dict = asdict(created_task)

        return jsonify(task_dict), 201

    def get(self, account_id: str, task_id: Optional[str] = None) -> ResponseReturnValue:
        if task_id:
            task_params = GetTaskParams(account_id=account_id, task_id=task_id)
            comments = CommentService.get_comments(params=task_params)
            return comments, 200
        else:
            page = request.args.get("page", type=int)
            size = request.args.get("size", type=int)

            if page is not None and page < 1:
                raise TaskBadRequestError("Page must be greater than 0")

            if size is not None and size < 1:
                raise TaskBadRequestError("Size must be greater than 0")

            if page is None:
                page = DEFAULT_PAGINATION_PARAMS.page
            if size is None:
                size = DEFAULT_PAGINATION_PARAMS.size

            pagination_params = PaginationParams(page=page, size=size, offset=0)
            tasks_params = GetPaginatedTasksParams(account_id=account_id, pagination_params=pagination_params)

            pagination_result = TaskService.get_paginated_tasks(params=tasks_params)

            response_data = asdict(pagination_result)

            return jsonify(response_data), 200

    @access_auth_middleware
    def patch(self, account_id: str, task_id: str, comment_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        update_task_params = UpdateCommentParams(
            account_id=account_id, task_id=task_id, comment_id=comment_id, text=request_data["text"]
        )

        updated_task = CommentService.update_comment(params=update_task_params)
        task_dict = asdict(updated_task)

        return jsonify(task_dict), 200

    @access_auth_middleware
    def delete(self, account_id: str, task_id: str, comment_id: str) -> ResponseReturnValue:
        delete_params = DeleteCommentParams(account_id=account_id, task_id=task_id, comment_id=comment_id)

        CommentService.delete_comment(params=delete_params)

        return "", 204
