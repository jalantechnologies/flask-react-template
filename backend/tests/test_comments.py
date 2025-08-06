import sys
import os
import pytest
import json

# Add root directory to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory test DB

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_add_comment(client):
    response = client.post('/comments/', json={
        "task_id": 1,
        "content": "Test comment"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["task_id"] == 1
    assert data["content"] == "Test comment"

def test_edit_comment(client):
    # First, create a comment
    response = client.post('/comments/', json={
        "task_id": 1,
        "content": "Initial"
    })
    comment_id = response.get_json()["id"]

    # Edit the comment
    response = client.put(f'/comments/{comment_id}', json={
        "content": "Updated"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["content"] == "Updated"

def test_delete_comment(client):
    # First, create a comment
    response = client.post('/comments/', json={
        "task_id": 1,
        "content": "To be deleted"
    })
    comment_id = response.get_json()["id"]

    # Delete the comment
    response = client.delete(f'/comments/{comment_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Comment deleted"
