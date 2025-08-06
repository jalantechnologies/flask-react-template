import * as React from 'react';

const Dashboard: React.FC = () => <div></div>;

export default Dashboard;

import React, { useEffect, useState } from "react";
import axios from "axios";

interface Task {
  task_id: string;
  account_id: string;
  title: string;
  description: string;
  comments?: string[];
}

const Dashboard: React.FC = () => {
  const accountId = "123"; // Hardcoded for now
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTask, setNewTask] = useState({ title: "", description: "" });
  const [editTaskId, setEditTaskId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const baseURL = `http://localhost:5000/accounts/${accountId}/tasks`;

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const res = await axios.get(baseURL);
      setTasks(res.data.tasks);
    } catch (err) {
      console.error("Error fetching tasks", err);
    }
    setLoading(false);
  };

  const handleAddTask = async () => {
    if (!newTask.title || !newTask.description) return;
    try {
      await axios.post(baseURL, {
        title: newTask.title,
        description: newTask.description,
        account_id: accountId,
        active: true,
      });
      setNewTask({ title: "", description: "" });
      fetchTasks();
    } catch (err) {
      console.error("Error adding task", err);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await axios.delete(`${baseURL}/${taskId}`);
      fetchTasks();
    } catch (err) {
      console.error("Error deleting task", err);
    }
  };

  const handleEditTask = async (taskId: string) => {
    try {
      await axios.patch(`${baseURL}/${taskId}`, {
        title: newTask.title,
        description: newTask.description,
      });
      setEditTaskId(null);
      setNewTask({ title: "", description: "" });
      fetchTasks();
    } catch (err) {
      console.error("Error editing task", err);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Task Dashboard</h2>

      <div style={{ marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="Title"
          value={newTask.title}
          onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
        />
        <input
          type="text"
          placeholder="Description"
          value={newTask.description}
          onChange={(e) =>
            setNewTask({ ...newTask, description: e.target.value })
          }
        />
        {editTaskId ? (
          <button onClick={() => handleEditTask(editTaskId)}>Update</button>
        ) : (
          <button onClick={handleAddTask}>Add Task</button>
        )}
      </div>

      {loading ? (
        <p>Loading tasks...</p>
      ) : (
        <ul>
          {tasks.map((task) => (
            <li key={task.task_id} style={{ marginBottom: "1rem" }}>
              <strong>{task.title}</strong>: {task.description}
              <br />
              <button
                onClick={() => {
                  setEditTaskId(task.task_id);
                  setNewTask({
                    title: task.title,
                    description: task.description,
                  });
                }}
              >
                Edit
              </button>
              <button onClick={() => handleDeleteTask(task.task_id)}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Dashboard;
