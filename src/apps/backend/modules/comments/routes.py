import json
import os
from datetime import datetime
from flask import request, jsonify
from . import comments_blueprint
import uuid

DB_FILE = os.path.join(os.path.dirname(__file__), 'comments_db.json')
TASKS_DB_FILE = os.path.join(os.path.dirname(__file__), 'tasks_db.json')

def read_tasks():
    if not os.path.exists(TASKS_DB_FILE):
        return []
    with open(TASKS_DB_FILE, 'r') as f:
        return json.load(f)

def read_comments():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def write_comments(comments):
    with open(DB_FILE, 'w') as f:
        json.dump(comments, f, indent=2)

@comments_blueprint.route('/', methods=['POST'])
def create_comment():
    data = request.get_json()
    task_id = data.get('task_id')
    content = data.get('content')

    if not task_id or not content:
        return jsonify({'error': 'task_id and content are required'}), 400

    comments = read_comments()
    new_comment = {
        "id": str(uuid.uuid4()),
        "task_id": task_id,
        "content": content,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    comments.append(new_comment)
    write_comments(comments)
    return jsonify(new_comment), 201

@comments_blueprint.route('/<comment_id>', methods=['GET'])
def get_comment(comment_id):
    comments = read_comments()
    comment = next((c for c in comments if c['id'] == comment_id), None)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    return jsonify(comment)

@comments_blueprint.route('/<comment_id>', methods=['PUT'])
def update_comment(comment_id):
    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({'error': 'content is required'}), 400

    comments = read_comments()
    for c in comments:
        if c['id'] == comment_id:
            c['content'] = content
            c['updated_at'] = datetime.utcnow().isoformat()
            write_comments(comments)
            return jsonify(c)
    return jsonify({'error': 'Comment not found'}), 404

@comments_blueprint.route('/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comments = read_comments()
    new_comments = [c for c in comments if c['id'] != comment_id]
    if len(new_comments) == len(comments):
        return jsonify({'error': 'Comment not found'}), 404

    write_comments(new_comments)
    return jsonify({'message': 'Comment deleted'}), 200

@comments_blueprint.route('/task/<task_id>', methods=['GET'])
def get_comments_for_task(task_id):
    comments = read_comments()
    task_comments = [c for c in comments if c['task_id'] == task_id]
    return jsonify(task_comments)

@comments_blueprint.route('/tasks', methods=['GET'])
def get_all_tasks():
    print("tasks")
    tasks = read_tasks()
    return jsonify(tasks), 200
