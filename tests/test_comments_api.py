# tests/test_comments_api.py
"""
Functional tests for the Comments API.

These tests run entirely in memory using mongomock, so no real MongoDB
instance is required. They verify that comment creation, listing,
updating, and deletion all behave as expected.
"""

import pytest
import mongomock
from src.main import create_app


@pytest.fixture
def app():
    """
    Create a Flask app configured for testing.

    Instead of connecting to a live MongoDB instance, this uses
    mongomock's in-memory client so all DB operations stay isolated.
    """
    mock_client = mongomock.MongoClient()
    config = {
        "TESTING": True,
        "MONGO_CLIENT": mock_client,
        "MONGO_DBNAME": "testdb",
    }

    app = create_app(config)
    yield app


@pytest.fixture
def client(app):
    """Provide a simple HTTP client for making API calls."""
    return app.test_client()


def test_create_and_list_comments(client):
    """Verify a comment can be created and then retrieved in a task list."""
    # Create a new comment
    create_response = client.post(
        "/api/tasks/42/comments",
        json={"content": "hello world", "author": "alice"},
    )
    assert create_response.status_code == 201
    created_comment = create_response.get_json()

    # Validate returned data
    assert created_comment["task_id"] == "42"
    assert created_comment["content"] == "hello world"

    # Fetch all comments for the same task
    list_response = client.get("/api/tasks/42/comments")
    assert list_response.status_code == 200

    comments = list_response.get_json()
    assert isinstance(comments, list)
    assert any(c["content"] == "hello world" for c in comments)


def test_update_and_delete_comment(client):
    """Test the update and delete lifecycle of a single comment."""
    # Step 1: create a comment
    post_response = client.post(
        "/api/tasks/1/comments", json={"content": "first version", "author": "bob"}
    )
    assert post_response.status_code == 201

    # Step 2: list and extract comment ID
    list_response = client.get("/api/tasks/1/comments")
    comments = list_response.get_json()
    assert comments and isinstance(comments, list)
    comment_id = comments[0]["id"]

    # Step 3: update comment content
    update_response = client.put(
        f"/api/comments/{comment_id}", json={"content": "updated version"}
    )
    assert update_response.status_code == 200

    # Step 4: confirm update persisted
    get_response = client.get(f"/api/comments/{comment_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["content"] == "updated version"

    # Step 5: delete the comment
    delete_response = client.delete(f"/api/comments/{comment_id}")
    assert delete_response.status_code in (200, 204)

    # Step 6: ensure it’s now gone
    missing_response = client.get(f"/api/comments/{comment_id}")
    assert missing_response.status_code == 404
