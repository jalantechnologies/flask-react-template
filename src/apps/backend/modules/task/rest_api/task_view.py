from dataclasses import asdict
from typing import Optional

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.application.common.constants import DEFAULT_PAGINATION_PARAMS
from modules.application.common.types import PaginationParams
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.task.errors import TaskBadRequestError
from modules.task.task_service import TaskService
from modules.task.types import (
    CreateTaskParams,
    DeleteTaskParams,
    GetPaginatedTasksParams,
    GetTaskParams,
    UpdateTaskParams,
)


class TaskView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise TaskBadRequestError("Request body is required")

        if not request_data.get("title"):
            raise TaskBadRequestError("Title is required")

        if not request_data.get("description"):
            raise TaskBadRequestError("Description is required")

        create_task_params = CreateTaskParams(
            account_id=account_id, title=request_data["title"], description=request_data["description"]
        )

        created_task = TaskService.create_task(params=create_task_params)
        task_dict = asdict(created_task)

        return jsonify(task_dict), 201

    @access_auth_middleware
    def get(self, account_id: str, task_id: Optional[str] = None) -> ResponseReturnValue:
        if task_id:
            task_params = GetTaskParams(account_id=account_id, task_id=task_id)
            task = TaskService.get_task(params=task_params)
            task_dict = asdict(task)
            return jsonify(task_dict), 200
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
    def patch(self, account_id: str, task_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise TaskBadRequestError("Request body is required")

        if not request_data.get("title"):
            raise TaskBadRequestError("Title is required")

        if not request_data.get("description"):
            raise TaskBadRequestError("Description is required")

        update_task_params = UpdateTaskParams(
            account_id=account_id, task_id=task_id, title=request_data["title"], description=request_data["description"]
        )

        updated_task = TaskService.update_task(params=update_task_params)
        task_dict = asdict(updated_task)

        return jsonify(task_dict), 200

    @access_auth_middleware
    def delete(self, account_id: str, task_id: str) -> ResponseReturnValue:
        delete_params = DeleteTaskParams(account_id=account_id, task_id=task_id)

        TaskService.delete_task(params=delete_params)

        return "", 204
