import unittest
import json
from server import app

class TaskManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.base_url = "/api/tasks"

    def test_add_task(self):
        response = self.app.post(self.base_url, json={"title": "Test Task"})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["title"], "Test Task")
        self.task_id = data["id"]

    def test_get_tasks(self):
        response = self.app.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_update_task(self):
        # Create task first
        post_res = self.app.post(self.base_url, json={"title": "Task to Update"})
        task = post_res.get_json()
        task_id = task["id"]

        # Update task
        response = self.app.put(f"{self.base_url}/{task_id}", json={"completed": True})
        self.assertEqual(response.status_code, 200)
        updated = response.get_json()
        self.assertTrue(updated["completed"])

    def test_delete_task(self):
        # Create task first
        post_res = self.app.post(self.base_url, json={"title": "Task to Delete"})
        task = post_res.get_json()
        task_id = task["id"]

        # Delete task
        response = self.app.delete(f"{self.base_url}/{task_id}")
        self.assertEqual(response.status_code, 204)

        # Check it’s gone
        response = self.app.get(self.base_url)
        tasks = response.get_json()
        self.assertNotIn(task_id, [t["id"] for t in tasks])

if __name__ == '__main__':
    unittest.main()
