import pytest
from app import create_app
from app.extensions import db
from app.models.comment import Comment

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_comment(client):
    response = client.post("/comments/", json={
        "task_id": 1,
        "text": "Hello from test"
    })
    assert response.status_code == 201
    assert response.get_json()["text"] == "Hello from test"

def test_get_all_comments(client):
    client.post("/comments/", json={"task_id": 1, "text": "One"})
    client.post("/comments/", json={"task_id": 1, "text": "Two"})

    response = client.get("/comments/")
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == 2

def test_get_comment_by_id(client):
    client.post("/comments/", json={"task_id": 1, "text": "Find me"})
    response = client.get("/comments/1")
    assert response.status_code == 200
    assert response.get_json()["text"] == "Find me"

def test_update_comment(client):
    client.post("/comments/", json={"task_id": 1, "text": "Old Text"})
    response = client.put("/comments/1", json={"text": "New Text"})
    assert response.status_code == 200
    assert response.get_json()["text"] == "New Text"

def test_delete_comment(client):
    client.post("/comments/", json={"task_id": 1, "text": "To delete"})
    response = client.delete("/comments/1")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Comment deleted"
