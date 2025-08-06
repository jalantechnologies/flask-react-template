def test_add_comment(client):
    response = client.post("/tasks/1/comments/", json={"content": "Hello"})
    assert response.status_code == 201
    assert response.get_json()["content"] == "Hello"

def test_get_comments(client):
    client.post("/tasks/1/comments/", json={"content": "Hi"})
    res = client.get("/tasks/1/comments/")
    assert res.status_code == 200
    assert len(res.get_json()) > 0

def test_update_comment(client):
    res = client.post("/tasks/1/comments/", json={"content": "Old"})
    comment_id = res.get_json()["id"]
    updated = client.put(f"/comments/{comment_id}/", json={"content": "Updated"})
    assert updated.status_code == 200
    assert updated.get_json()["content"] == "Updated"

def test_delete_comment(client):
    res = client.post("/tasks/1/comments/", json={"content": "To delete"})
    comment_id = res.get_json()["id"]
    deleted = client.delete(f"/comments/{comment_id}/")
    assert deleted.status_code == 200
