from flask import Blueprint, request, jsonify
from app import db
from models.task import Task

task_bp = Blueprint('task_bp', __name__)

# GET /api/tasks
@task_bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description
    } for task in tasks])

# POST /api/tasks
@task_bp.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    task = Task(title=data['title'], description=data['description'])
    db.session.add(task)
    db.session.commit()
    return jsonify({'id': task.id, 'message': 'Task created'}), 201

# PUT /api/tasks/<id>
@task_bp.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    task.title = data['title']
    task.description = data['description']
    db.session.commit()
    return jsonify({'message': 'Task updated'})

# DELETE /api/tasks/<id>
@task_bp.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})
