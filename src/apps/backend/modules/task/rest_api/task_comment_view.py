from datetime import datetime
from typing import Optional

from bson.objectid import ObjectId
from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.task.errors import TaskBadRequestError, TaskNotFoundError
from modules.task.internal.store.task_repository import TaskRepository


class TaskCommentView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str, task_id: str) -> ResponseReturnValue:
        request_data = request.get_json()
        if request_data is None:
            raise TaskBadRequestError("Request body is required")
        text = request_data.get("text")
        if not text:
            raise TaskBadRequestError("Text is required")

        task_bson = TaskRepository.collection().find_one(
            {
                "_id": ObjectId(task_id),
                "account_id": account_id,
                "active": True,
            }
        )
        if task_bson is None:
            raise TaskNotFoundError(task_id=task_id)

        now = datetime.now()
        comment_id = str(ObjectId())
        new_comment = {
            "id": comment_id,
            "text": text,
            "created_at": now,
            "updated_at": now,
        }

        TaskRepository.collection().update_one(
            {"_id": ObjectId(task_id), "comments": None},
            {"$set": {"comments": []}},
        )

        TaskRepository.collection().update_one(
            {"_id": ObjectId(task_id)},
            {
                "$push": {"comments": new_comment},
                "$set": {"updated_at": now},
            },
        )

        response_comment = {
            "id": comment_id,
            "task_id": task_id,
            "account_id": account_id,
            "text": text,
        }
        return jsonify(response_comment), 201

    @access_auth_middleware
    def get(
        self,
        account_id: str,
        task_id: str,
        comment_id: Optional[str] = None,
    ) -> ResponseReturnValue:
        task_bson = TaskRepository.collection().find_one(
            {
                "_id": ObjectId(task_id),
                "account_id": account_id,
                "active": True,
            }
        )
        if task_bson is None:
            raise TaskNotFoundError(task_id=task_id)

        comments = task_bson.get("comments") or []

        if comment_id is not None:
            for comment in comments:
                if comment.get("id") == comment_id:
                    response_comment = {
                        "id": comment.get("id"),
                        "task_id": task_id,
                        "account_id": account_id,
                        "text": comment.get("text", ""),
                    }
                    return jsonify(response_comment), 200
            raise TaskNotFoundError(task_id=task_id)

        items = [
            {
                "id": comment.get("id"),
                "task_id": task_id,
                "account_id": account_id,
                "text": comment.get("text", ""),
            }
            for comment in comments
        ]
        response_data = {
            "items": items,
            "total_count": len(items),
        }
        return jsonify(response_data), 200

    @access_auth_middleware
    def patch(
        self,
        account_id: str,
        task_id: str,
        comment_id: str,
    ) -> ResponseReturnValue:
        request_data = request.get_json()
        if request_data is None:
            raise TaskBadRequestError("Request body is required")
        text = request_data.get("text")
        if not text:
            raise TaskBadRequestError("Text is required")

        now = datetime.now()
        result = TaskRepository.collection().update_one(
            {
                "_id": ObjectId(task_id),
                "account_id": account_id,
                "active": True,
                "comments.id": comment_id,
            },
            {
                "$set": {
                    "comments.$.text": text,
                    "comments.$.updated_at": now,
                    "updated_at": now,
                }
            },
        )

        if result.matched_count == 0:
            raise TaskNotFoundError(task_id=task_id)

        task_bson = TaskRepository.collection().find_one(
            {
                "_id": ObjectId(task_id),
                "account_id": account_id,
                "active": True,
            }
        )
        if task_bson is None:
            raise TaskNotFoundError(task_id=task_id)

        comments = task_bson.get("comments") or []
        updated_comment = None
        for comment in comments:
            if comment.get("id") == comment_id:
                updated_comment = comment
                break

        if updated_comment is None:
            raise TaskNotFoundError(task_id=task_id)

        response_comment = {
            "id": updated_comment.get("id"),
            "task_id": task_id,
            "account_id": account_id,
            "text": updated_comment.get("text", ""),
        }
        return jsonify(response_comment), 200

    @access_auth_middleware
    def delete(
        self,
        account_id: str,
        task_id: str,
        comment_id: str,
    ) -> ResponseReturnValue:
        TaskRepository.collection().update_one(
            {"_id": ObjectId(task_id), "comments": None},
            {"$set": {"comments": []}},
        )

        result = TaskRepository.collection().update_one(
            {
                "_id": ObjectId(task_id),
                "account_id": account_id,
                "active": True,
            },
            {
                "$pull": {"comments": {"id": comment_id}},
            },
        )

        if result.matched_count == 0 or result.modified_count == 0:
            raise TaskNotFoundError(task_id=task_id)

        return "", 204
