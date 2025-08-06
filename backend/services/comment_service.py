from extensions import db
from models.comment import Comment

def create_comment(task_id, content):
    comment = Comment(task_id=task_id, content=content)
    db.session.add(comment)
    db.session.commit()
    return comment

def get_all_comments():
    return Comment.query.all()

def update_comment(comment_id, content):
    comment = Comment.query.get(comment_id)
    if comment:
        comment.content = content
        db.session.commit()
    return comment

def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment:
        db.session.delete(comment)
        db.session.commit()
    return comment
