import json
from bson import ObjectId


def test_create_comment(client):
    task_id = str(ObjectId())
    data = {
        "task_id": task_id,
        "author": "Test User",
        "content": "This is a test comment."
    }
    response = client.post("/comments", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    assert "id" in response.json


def test_get_comments_by_task(client):
    task_id = str(ObjectId())

    # Create 2 comments
    for i in range(2):
        data = {
            "task_id": task_id,
            "author": f"Tester {i}",
            "content": f"Comment {i}"
        }
        client.post("/comments", data=json.dumps(data), content_type='application/json')

    response = client.get(f"/comments/task/{task_id}")
    assert response.status_code == 200
    assert len(response.json) == 2


def test_update_comment(client):
    # First create a comment
    task_id = str(ObjectId())
    data = {
        "task_id": task_id,
        "author": "Tester",
        "content": "Initial content"
    }
    create_resp = client.post("/comments", data=json.dumps(data), content_type='application/json')
    comment_id = create_resp.json["id"]

    # Now update it
    update_data = {
        "content": "Updated content"
    }
    response = client.put(f"/comments/{comment_id}", data=json.dumps(update_data), content_type='application/json')
    assert response.status_code == 200
    assert response.json["message"] == "Comment updated"


def test_delete_comment(client):
    # First create a comment
    task_id = str(ObjectId())
    data = {
        "task_id": task_id,
        "author": "Tester",
        "content": "To be deleted"
    }
    create_resp = client.post("/comments", data=json.dumps(data), content_type='application/json')
    comment_id = create_resp.json["id"]

    # Now delete it
    response = client.delete(f"/comments/{comment_id}")
    assert response.status_code == 200
    assert response.json["message"] == "Comment deleted"
