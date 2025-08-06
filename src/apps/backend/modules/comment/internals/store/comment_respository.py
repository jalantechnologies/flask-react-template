from .comment_model import Comment
from app.backend.db import db

def save(comment):
    db.session.add(comment)
    db.session.commit()
    return comment

def delete(comment):
    db.session.delete(comment)
    db.session.commit()

def find_by_task_id(task_id):
    return Comment.query.filter_by(task_id=task_id).all()

def find_by_id(comment_id):
    return Comment.query.get(comment_id)
