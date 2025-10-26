from modules.comment.internal.comment_reader import CommentReader
from modules.comment.internal.comment_writer import CommentWriter
from modules.comment.types import CreateCommentParams, DeleteCommentParams, UpdateCommentParams
from modules.task.internal.task_reader import TaskReader
from modules.task.types import GetTaskParams, Task, TaskDeletionResult


class CommentService:
    @staticmethod
    #  Get the Comments of a Task
    def create_comment(*, params: CreateCommentParams) -> Task:
        try:
            TaskReader.get_task(params=GetTaskParams(account_id=params.account_id, task_id=params.task_id))
        except Exception as e:
            return {"key": "Task is not found" + str(e)}
        return CommentWriter.create_comment(params=params)

    @staticmethod
    # GetTaskParams -> using it to get all the comments
    def get_comments(*, params: GetTaskParams) -> Task:
        comments = CommentReader.get_comment(params=params)
        return comments

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Task:
        return CommentWriter.update_comment(params=params)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> TaskDeletionResult:
        return CommentWriter.delete_comment(params=params)
