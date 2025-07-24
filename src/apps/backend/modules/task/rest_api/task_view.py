from dataclasses import asdict
from typing import Optional

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

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
    def post(self) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise TaskBadRequestError("Request body is required")

        if not request_data.get("title"):
            raise TaskBadRequestError("Title is required")

        if not request_data.get("description"):
            raise TaskBadRequestError("Description is required")

        task_params = CreateTaskParams(
            account_id=getattr(request, "account_id"),
            title=request_data["title"],
            description=request_data["description"],
        )

        task = TaskService.create_task(params=task_params)
        task_dict = asdict(task)

        return jsonify(task_dict), 201

    @access_auth_middleware
    def get(self, task_id: Optional[str] = None) -> ResponseReturnValue:
        if task_id:
            task_params = GetTaskParams(account_id=getattr(request, "account_id"), task_id=task_id)
            task = TaskService.get_task_for_account(params=task_params)
            task_dict = asdict(task)
            return jsonify(task_dict), 200
        else:
            page = request.args.get("page", type=int)
            size = request.args.get("size", type=int)

            tasks_params = GetPaginatedTasksParams(account_id=getattr(request, "account_id"), page=page, size=size)

            pagination_result = TaskService.get_paginated_tasks_for_account(params=tasks_params)

            response_data = {
                "items": [asdict(task) for task in pagination_result.items],
                "pagination": {
                    "page": pagination_result.pagination_params.page,
                    "size": pagination_result.pagination_params.size,
                    "total_count": pagination_result.total_count,
                    "total_pages": pagination_result.total_pages,
                },
            }

            return jsonify(response_data), 200

    @access_auth_middleware
    def patch(self, task_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise TaskBadRequestError("Request body is required")

        if not request_data.get("title"):
            raise TaskBadRequestError("Title is required")

        if not request_data.get("description"):
            raise TaskBadRequestError("Description is required")

        update_params = UpdateTaskParams(
            account_id=getattr(request, "account_id"),
            task_id=task_id,
            title=request_data["title"],
            description=request_data["description"],
        )

        updated_task = TaskService.update_task(params=update_params)
        task_dict = asdict(updated_task)

        return jsonify(task_dict), 200

    @access_auth_middleware
    def delete(self, task_id: str) -> ResponseReturnValue:
        delete_params = DeleteTaskParams(account_id=getattr(request, "account_id"), task_id=task_id)

        TaskService.delete_task(params=delete_params)

        return "", 204
