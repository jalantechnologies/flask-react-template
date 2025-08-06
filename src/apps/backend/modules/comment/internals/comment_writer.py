from .store import comment_repository
from .store.comment_model import Comment

def create_comment(content, task_id):
    comment = Comment(content=content, task_id=task_id)
    return comment_repository.save(comment)

def update_comment(comment_id, content):
    comment = comment_repository.find_by_id(comment_id)
    if not comment:
        raise Exception("Comment not found")
    comment.content = content
    return comment_repository.save(comment)

def delete_comment(comment_id):
    comment = comment_repository.find_by_id(comment_id)
    if not comment:
        raise Exception("Comment not found")
    comment_repository.delete(comment)
