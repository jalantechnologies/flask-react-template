from datetime import datetime

from bson.objectid import ObjectId
from pymongo import ReturnDocument

from modules.task.errors import TaskNotFoundError
from modules.task.internal.store.task_model import TaskModel
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.internal.task_reader import TaskReader
from modules.task.internal.task_util import TaskUtil
from modules.task.types import (
    CreateTaskParams,
    DeleteTaskParams,
    GetTaskParams,
    Task,
    TaskDeletionResult,
    UpdateTaskParams,
)


class TaskWriter:
    @staticmethod
    def create_task(*, params: CreateTaskParams) -> Task:
        task_bson = TaskModel(
            account_id=params.account_id, description=params.description, title=params.title
        ).to_bson()

        query = TaskRepository.collection().insert_one(task_bson)
        created_task_bson = TaskRepository.collection().find_one({"_id": query.inserted_id})

        return TaskUtil.convert_task_bson_to_task(created_task_bson)

    @staticmethod
    def update_task(*, params: UpdateTaskParams) -> Task:
        updated_task_bson = TaskRepository.collection().find_one_and_update(
            {"_id": ObjectId(params.task_id), "account_id": params.account_id, "active": True},
            {"$set": {"description": params.description, "title": params.title, "updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER,
        )

        if updated_task_bson is None:
            raise TaskNotFoundError(task_id=params.task_id)

        return TaskUtil.convert_task_bson_to_task(updated_task_bson)

    @staticmethod
    def delete_task(*, params: DeleteTaskParams) -> TaskDeletionResult:
        task = TaskReader.get_task(params=GetTaskParams(account_id=params.account_id, task_id=params.task_id))

        deletion_time = datetime.now()
        updated_task_bson = TaskRepository.collection().find_one_and_update(
            {"_id": ObjectId(task.id)},
            {"$set": {"active": False, "updated_at": deletion_time}},
            return_document=ReturnDocument.AFTER,
        )

        if updated_task_bson is None:
            raise TaskNotFoundError(task_id=params.task_id)

        return TaskDeletionResult(task_id=params.task_id, deleted_at=deletion_time, success=True)
