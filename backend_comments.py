# backend_comments.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize database
db = SQLAlchemy()

# ------------------ MODELS ------------------

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    comments = db.relationship('Comment', backref='task', cascade="all, delete-orphan", lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)

# ------------------ CREATE APP ------------------

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    # Default configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Override with test config if provided
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    # Create tables automatically
    with app.app_context():
        db.create_all()

    # ------------------ TASK ROUTES ------------------

    @app.route('/tasks', methods=['GET'])
    def get_tasks():
        tasks = Task.query.all()
        return jsonify([{'id': t.id, 'title': t.title} for t in tasks])

    @app.route('/tasks', methods=['POST'])
    def create_task():
        data = request.get_json()
        title = data.get('title')
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        task = Task(title=title)
        db.session.add(task)
        db.session.commit()
        return jsonify({'id': task.id, 'title': task.title}), 201

    @app.route('/tasks/<int:id>', methods=['PUT'])
    def update_task(id):
        task = Task.query.get_or_404(id)
        data = request.get_json()
        task.title = data.get('title', task.title)
        db.session.commit()
        return jsonify({'id': task.id, 'title': task.title})

    @app.route('/tasks/<int:id>', methods=['DELETE'])
    def delete_task(id):
        task = Task.query.get_or_404(id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'})

    # ------------------ COMMENT ROUTES ------------------

    @app.route('/tasks/<int:task_id>/comments', methods=['GET'])
    def get_comments(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        comments = Comment.query.filter_by(task_id=task_id).all()
        return jsonify([{'id': c.id, 'author': c.author, 'body': c.body, 'task_id': c.task_id} for c in comments])

    @app.route('/tasks/<int:task_id>/comments', methods=['POST'])
    def add_comment(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        data = request.get_json()
        author = data.get('author')
        body = data.get('body')
        if not author or not body:
            return jsonify({'error': 'Author and body are required'}), 400
        comment = Comment(task_id=task_id, author=author, body=body)
        db.session.add(comment)
        db.session.commit()
        return jsonify({'id': comment.id, 'author': comment.author, 'body': comment.body, 'task_id': comment.task_id}), 201

    @app.route('/comments/<int:id>', methods=['GET'])
    def get_comment(id):
        comment = Comment.query.get_or_404(id)
        return jsonify({'id': comment.id, 'author': comment.author, 'body': comment.body, 'task_id': comment.task_id})

    @app.route('/comments/<int:id>', methods=['PUT'])
    def update_comment(id):
        comment = Comment.query.get_or_404(id)
        data = request.get_json()
        if not data or ('author' not in data and 'body' not in data):
            return jsonify({'error': 'Nothing to update'}), 400
        comment.author = data.get('author', comment.author)
        comment.body = data.get('body', comment.body)
        db.session.commit()
        return jsonify({'id': comment.id, 'author': comment.author, 'body': comment.body, 'task_id': comment.task_id})

    @app.route('/comments/<int:id>', methods=['DELETE'])
    def delete_comment(id):
        comment = Comment.query.get_or_404(id)
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': 'Comment deleted successfully'})

    return app

# ------------------ MAIN ------------------

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
