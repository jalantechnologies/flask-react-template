from modules.application.repository import ApplicationRepository
from modules.comment.internal.store.comment_model import CommentModel


class CommentRepository(ApplicationRepository):

    collection_name = "comments"  # Class attribute - required by ApplicationRepository

    def __init__(self):
        super().__init__()  # Call the parent constructor
        self.model_class = CommentModel

    @staticmethod
    def on_init_collection(collection):
        # Create indexes for efficient queries - collection is passed as parameter
        collection.create_index("task_id")
        collection.create_index("account_id")
        collection.create_index([("task_id", 1), ("created_at", -1)])
