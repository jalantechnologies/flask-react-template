const API_BASE_URL = "http://localhost:5000/api";

export async function getTasks() {
  const res = await fetch(`${API_BASE_URL}/tasks`);
  return res.json();
}

export async function createTask(title: string) {
  const res = await fetch(`${API_BASE_URL}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  return res.json();
}

export async function updateTask(id: number, title: string) {
  const res = await fetch(`${API_BASE_URL}/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  return res.json();
}

export async function deleteTask(id: number) {
  await fetch(`${API_BASE_URL}/tasks/${id}`, {
    method: "DELETE",
  });
}
