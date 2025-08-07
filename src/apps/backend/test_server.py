import pytest
from comment_server import app, _comments_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def run_around_tests():
    _comments_db.clear()
    yield

def test_post_comment(client):
    comment_data = {
        "author_id": "test_user_1",
        "text": "This is a test comment from a test!"
    }
    response = client.post("/api/comments/for-task/test-task-1", json=comment_data)
    assert response.status_code == 201
    
    response_json = response.get_json()
    assert response_json['author_id'] == "test_user_1"
    assert response_json['text'] == "This is a test comment from a test!"

def test_get_comments(client):
    comment_data = {
        "author_id": "test_user_2",
        "text": "Another test comment."
    }
    client.post("/api/comments/for-task/test-task-1", json=comment_data)
    
    response = client.get("/api/comments/for-task/test-task-1")
    assert response.status_code == 200
    
    response_json = response.get_json()
    assert isinstance(response_json, list)
    assert len(response_json) == 1

def test_put_comment(client):
    comment_data = {
        "author_id": "test_user_3",
        "text": "Comment to be updated."
    }
    post_response = client.post("/api/comments/for-task/test-task-1", json=comment_data)
    comment_id = post_response.get_json()['id']

    updated_data = {
        "text": "This comment has been updated by a test!"
    }
    response = client.put(f"/api/comments/{comment_id}", json=updated_data)
    assert response.status_code == 200
    
    response_json = response.get_json()
    assert response_json['text'] == "This comment has been updated by a test!"

def test_delete_comment(client):
    comment_data = {
        "author_id": "test_user_4",
        "text": "Comment to be deleted."
    }
    post_response = client.post("/api/comments/for-task/test-task-1", json=comment_data)
    comment_id = post_response.get_json()['id']
    
    response = client.delete(f"/api/comments/{comment_id}")
    assert response.status_code == 204
    
    get_response = client.get("/api/comments/for-task/test-task-1")
    get_response_json = get_response.get_json()
    assert len(get_response_json) == 0