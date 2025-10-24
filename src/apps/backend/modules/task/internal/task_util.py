from typing import Any

from modules.task.internal.store.task_model import TaskModel
from modules.task.types import Task


class TaskUtil:
    @staticmethod
    def convert_task_bson_to_task(task_bson: dict[str, Any]) -> Task:
        validated_task_data = TaskModel.from_bson(task_bson)
        return Task(
            account_id=validated_task_data.account_id,
            description=validated_task_data.description,
            id=str(validated_task_data.id),
            title=validated_task_data.title,
        )
