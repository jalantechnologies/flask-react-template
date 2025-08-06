from .store import comment_repository

def get_comments_by_task(task_id):
    return comment_repository.find_by_task_id(task_id)
