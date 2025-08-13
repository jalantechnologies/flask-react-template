from src import db
from datetime import datetime
import uuid

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
