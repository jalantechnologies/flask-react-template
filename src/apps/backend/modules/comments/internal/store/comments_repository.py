from modules.application.repository import ApplicationRepository


class CommentRepository(ApplicationRepository):
    def collection(self):
        return super().get_collection("comments")

    def on_init_collection(self):
        # Add indexes or validation if needed
        pass
