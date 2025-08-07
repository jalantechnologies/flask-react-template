from src.apps.backend.modules.comment.comment_model import Comment
from app import db

def create_comment(task_id, content):
    comment = Comment(task_id=task_id, content=content)
    db.session.add(comment)
    db.session.commit()
    return comment

def get_all_comments():
    return Comment.query.all()

def get_comment_by_id(comment_id):
    return Comment.query.get_or_404(comment_id)

def update_comment(comment_id, new_content):
    comment = get_comment_by_id(comment_id)
    comment.content = new_content
    db.session.commit()
    return comment

def delete_comment(comment_id):
    comment = get_comment_by_id(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return True
