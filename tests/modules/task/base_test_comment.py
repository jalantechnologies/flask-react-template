from bson import ObjectId

from modules.application.common.types import PaginationParams
from modules.task.internal.store.comment_model import CommentModel
from modules.task.internal.store.comment_repository import CommentRepository
from modules.task.internal.store.task_model import TaskModel
from modules.task.internal.store.task_repository import TaskRepository
from tests.modules.task.base_test_task import BaseTestTask


class BaseTestComment(BaseTestTask):
    def setUp(self):
        super().setUp()
        self.comment_repository = CommentRepository()
        self.task_repository = TaskRepository()

    def tearDown(self):
        super().tearDown()
        CommentRepository.collection().delete_many({})

    def create_test_task(self, account_id: str = "test_account_id") -> TaskModel:
        task_model = TaskModel(account_id=account_id, title="Test Task", description="Test Description")
        task_bson = task_model.to_bson()
        query = TaskRepository.collection().insert_one(task_bson)
        created_task_bson = TaskRepository.collection().find_one({"_id": query.inserted_id})
        return TaskModel.from_bson(created_task_bson)

    def create_test_comment(
        self, task_id: str, account_id: str = "test_account_id", content: str = "Test Comment"
    ) -> CommentModel:
        comment_model = CommentModel(task_id=task_id, account_id=account_id, content=content)
        comment_bson = comment_model.to_bson()
        query = CommentRepository.collection().insert_one(comment_bson)
        created_comment_bson = CommentRepository.collection().find_one({"_id": query.inserted_id})
        return CommentModel.from_bson(created_comment_bson)

    def get_comment_by_id(self, comment_id: str) -> CommentModel:
        comment_bson = CommentRepository.collection().find_one({"_id": ObjectId(comment_id), "active": True})
        if not comment_bson:
            return None
        return CommentModel.from_bson(comment_bson)

    def get_comments_by_task_id(self, task_id: str) -> list[CommentModel]:
        comment_bsons = list(
            CommentRepository.collection().find({"task_id": task_id, "active": True}, sort=[("created_at", -1)])
        )
        return [CommentModel.from_bson(comment_bson) for comment_bson in comment_bsons]

    def delete_comment(self, comment_id: str) -> bool:
        result = CommentRepository.collection().update_one(
            {"_id": ObjectId(comment_id), "active": True}, {"$set": {"active": False}}
        )
        return result.modified_count > 0

    def count_comments_by_task_id(self, task_id: str) -> int:
        return CommentRepository.collection().count_documents({"task_id": task_id, "active": True})

    def create_pagination_params(self, page: int = 1, size: int = 10) -> PaginationParams:
        return PaginationParams(page=page, size=size, offset=0)
