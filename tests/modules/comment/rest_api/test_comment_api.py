import json

def test_add_comment(client):
    # Sample request payload
    payload = {
        "user_id": 1,
        "task_id": 1,
        "text": "This is a test comment"
    }

    # Send POST request
    response = client.post("/api/comments", data=json.dumps(payload), content_type="application/json")

    # Assertions
    assert response.status_code == 201  # Assuming 201 Created
    data = response.get_json()
    
    assert "id" in data
    assert data["text"] == payload["text"]
    assert data["user_id"] == payload["user_id"]
    assert data["task_id"] == payload["task_id"]
def test_update_comment(client):
    # First, add a comment to update
    payload = {
        "user_id": 1,
        "task_id": 1,
        "text": "Original comment"
    }
    post_response = client.post("/api/comments", data=json.dumps(payload), content_type="application/json")
    comment_id = post_response.get_json()["id"]

    # Now, update the comment
    updated_payload = {
        "text": "Updated comment text"
    }
    put_response = client.put(f"/api/comments/{comment_id}", data=json.dumps(updated_payload), content_type="application/json")

    # Assertions
    assert put_response.status_code == 200
    updated_data = put_response.get_json()

    assert updated_data["id"] == comment_id
    assert updated_data["text"] == updated_payload["text"]
def test_delete_comment(client):
    # First, add a comment to delete
    payload = {
        "user_id": 1,
        "task_id": 1,
        "text": "Comment to be deleted"
    }
    post_response = client.post("/api/comments", data=json.dumps(payload), content_type="application/json")
    comment_id = post_response.get_json()["id"]

    # Now, delete the comment
    delete_response = client.delete(f"/api/comments/{comment_id}")

    # Assertions
    assert delete_response.status_code == 204  # No Content

    # Optionally, confirm it's gone (if your app returns 404 after deletion)
    get_response = client.get(f"/api/tasks/1/comments")
    data = get_response.get_json()

    # The deleted comment should not be in the list
    assert all(comment["id"] != comment_id for comment in data)
def test_list_comments(client):
    # Clear existing comments (if any added by previous tests in same session)
    # Add multiple comments for task_id = 1
    comments = [
        {"user_id": 1, "task_id": 1, "text": "First comment"},
        {"user_id": 1, "task_id": 1, "text": "Second comment"}
    ]

    for comment in comments:
        client.post("/api/comments", data=json.dumps(comment), content_type="application/json")

    # Fetch comments for task_id = 1
    response = client.get("/api/tasks/1/comments")

    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2  # You can make it `== 2` if the DB is clean each time

    texts = [c["text"] for c in data]
    assert "First comment" in texts
    assert "Second comment" in texts
