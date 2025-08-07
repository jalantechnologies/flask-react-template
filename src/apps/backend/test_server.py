import pytest
from comment_server import app, _comments_db  # Import your Flask app and the temporary db

# Create a test client using a pytest fixture
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# This fixture will automatically clear the database before each test
@pytest.fixture(autouse=True)
def run_around_tests():
    _comments_db.clear()
    yield

# --- Test the POST Endpoint (Create a comment) ---
def test_post_comment(client):
    # Data to send in the POST request
    comment_data = {
        "author_id": "test_user_1",
        "text": "This is a test comment from a test!"
    }
    # Send the POST request to the /comments/for-task/ endpoint
    response = client.post("/api/comments/for-task/test-task-1", json=comment_data)

    # Check that the response is successful (201 Created)
    assert response.status_code == 201
    
    # Check that the response body contains the data we sent
    response_json = response.get_json()
    assert response_json['author_id'] == "test_user_1"
    assert response_json['text'] == "This is a test comment from a test!"

# --- Test the GET Endpoint (Retrieve comments) ---
def test_get_comments(client):
    # First, post a new comment to make sure there's data to retrieve
    comment_data = {
        "author_id": "test_user_2",
        "text": "Another test comment."
    }
    client.post("/api/comments/for-task/test-task-1", json=comment_data)
    
    # Send the GET request to the /comments/for-task/ endpoint
    response = client.get("/api/comments/for-task/test-task-1")

    # Check that the response is successful (200 OK)
    assert response.status_code == 200
    
    # Check that the response is a list and contains our comment
    response_json = response.get_json()
    assert isinstance(response_json, list)
    assert len(response_json) == 1

# --- Test the PUT Endpoint (Update a comment) ---
def test_put_comment(client):
    # First, post a new comment to get a comment ID
    comment_data = {
        "author_id": "test_user_3",
        "text": "Comment to be updated."
    }
    post_response = client.post("/api/comments/for-task/test-task-1", json=comment_data)
    comment_id = post_response.get_json()['id']

    # Data to send in the PUT request
    updated_data = {
        "text": "This comment has been updated by a test!"
    }
    # Send the PUT request to the /comments/ endpoint
    response = client.put(f"/api/comments/{comment_id}", json=updated_data)

    # Check that the response is successful (200 OK)
    assert response.status_code == 200
    
    # Check that the response body has the updated text
    response_json = response.get_json()
    assert response_json['text'] == "This comment has been updated by a test!"

# --- Test the DELETE Endpoint (Delete a comment) ---
def test_delete_comment(client):
    # First, post a new comment to get a comment ID
    comment_data = {
        "author_id": "test_user_4",
        "text": "Comment to be deleted."
    }
    post_response = client.post("/api/comments/for-task/test-task-1", json=comment_data)
    comment_id = post_response.get_json()['id']
    
    # Send the DELETE request to the /comments/ endpoint
    response = client.delete(f"/api/comments/{comment_id}")

    # Check that the response is successful (204 No Content)
    assert response.status_code == 204
    
    # Check that the comment is actually gone
    get_response = client.get("/api/comments/for-task/test-task-1")
    get_response_json = get_response.get_json()
    assert len(get_response_json) == 0