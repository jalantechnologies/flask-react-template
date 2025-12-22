import React, { useEffect, useState } from "react";
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
} from "../../services/task.service";

type Task = {
  id: number;
  title: string;
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTitle, setNewTitle] = useState("");

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (error) {
      console.error("Failed to fetch tasks", error);
    }
  };

  const handleAddTask = async () => {
    if (!newTitle.trim()) return;

    try {
      await createTask(newTitle);
      setNewTitle("");
      fetchTasks();
    } catch (error) {
      console.error("Failed to create task", error);
    }
  };

  const handleUpdateTask = async (id: number, title: string) => {
    const updatedTitle = prompt("Update task title", title);
    if (!updatedTitle || !updatedTitle.trim()) return;

    try {
      await updateTask(id, updatedTitle);
      fetchTasks();
    } catch (error) {
      console.error("Failed to update task", error);
    }
  };

  const handleDeleteTask = async (id: number) => {
    const confirmDelete = window.confirm("Are you sure you want to delete this task?");
    if (!confirmDelete) return;

    try {
      await deleteTask(id);
      fetchTasks();
    } catch (error) {
      console.error("Failed to delete task", error);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "40px auto" }}>
      <h2>Tasks</h2>

      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        <input
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="New task title"
          style={{ flex: 1, padding: 8 }}
        />
        <button onClick={handleAddTask}>Add</button>
      </div>

      <ul>
        {tasks.map((task) => (
          <li key={task.id} style={{ marginBottom: 10 }}>
            <strong>{task.title}</strong>{" "}
            <button onClick={() => handleUpdateTask(task.id, task.title)}>
              Edit
            </button>{" "}
            <button onClick={() => handleDeleteTask(task.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
