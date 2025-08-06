from server import app

from .base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):
    def setUp(self):
        super().setUp()
        self.account = self.create_test_account()
        self.task = self.create_test_task(self.account.id)
        self.token = self.get_access_token()
        self.headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}

    def test_add_comment(self):
        with app.test_client() as client:
            response = client.post(
                f"/api/tasks/{self.task.id}/comments", headers=self.headers, json={"content": "This is a test comment"}
            )
            assert response.status_code == 201
            data = response.get_json()
            assert data["content"] == "This is a test comment"
            assert data["task_id"] == str(self.task.id)

    def test_list_comments(self):
        # Add a comment first
        with app.test_client() as client:
            client.post(f"/api/tasks/{self.task.id}/comments", headers=self.headers, json={"content": "Comment 1"})
            client.post(f"/api/tasks/{self.task.id}/comments", headers=self.headers, json={"content": "Comment 2"})
            response = client.get(f"/api/tasks/{self.task.id}/comments", headers=self.headers)
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 2
            assert data[0]["task_id"] == str(self.task.id)

    def test_edit_comment(self):
        # Add a comment first
        with app.test_client() as client:
            add_resp = client.post(
                f"/api/tasks/{self.task.id}/comments", headers=self.headers, json={"content": "Original comment"}
            )
            comment_id = add_resp.get_json()["id"]
            # Edit
            response = client.put(
                f"/api/comments/{comment_id}", headers=self.headers, json={"content": "Edited comment"}
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["content"] == "Edited comment"

    def test_delete_comment(self):
        # Add a comment first
        with app.test_client() as client:
            add_resp = client.post(
                f"/api/tasks/{self.task.id}/comments", headers=self.headers, json={"content": "To be deleted"}
            )
            comment_id = add_resp.get_json()["id"]
            # Delete
            response = client.delete(f"/api/comments/{comment_id}", headers=self.headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
