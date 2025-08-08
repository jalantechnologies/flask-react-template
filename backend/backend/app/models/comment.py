from app import db
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False)  # 👈 this line is missing or broken
    text = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"<Comment {self.id}>"
