import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

const App = () => {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [editId, setEditId] = useState(null);

  const fetchTasks = () => {
    fetch('/api/tasks')
      .then(res => res.json())
      .then(data => setTasks(data));
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleCreate = () => {
    fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description: desc })
    }).then(() => {
      setTitle('');
      setDesc('');
      fetchTasks();
    });
  };

  const handleUpdate = () => {
    fetch(`/api/tasks/${editId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description: desc })
    }).then(() => {
      setEditId(null);
      setTitle('');
      setDesc('');
      fetchTasks();
    });
  };

  const handleDelete = (id) => {
    fetch(`/api/tasks/${id}`, { method: 'DELETE' })
      .then(() => fetchTasks());
  };

  const handleToggleComplete = (task) => {
    fetch(`/api/tasks/${task.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed: !task.completed })
    }).then(fetchTasks);
  };

  const handleEdit = (task) => {
    setEditId(task.id);
    setTitle(task.title);
    setDesc(task.description);
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h2>📝 Task Manager</h2>
      <input
        placeholder="Title"
        value={title}
        onChange={e => setTitle(e.target.value)}
        style={{ marginRight: "10px" }}
      />
      <input
        placeholder="Description"
        value={desc}
        onChange={e => setDesc(e.target.value)}
        style={{ marginRight: "10px" }}
      />
      <button onClick={editId ? handleUpdate : handleCreate}>
        {editId ? 'Update Task' : 'Add Task'}
      </button>

      <ul style={{ marginTop: "20px" }}>
        {tasks.map(task => (
          <li key={task.id} style={{ marginBottom: "10px" }}>
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => handleToggleComplete(task)}
            />
            <b style={{ textDecoration: task.completed ? 'line-through' : 'none' }}>
              {task.title}
            </b> - {task.description}
            <button onClick={() => handleEdit(task)} style={{ marginLeft: "10px" }}>Edit</button>
            <button onClick={() => handleDelete(task.id)} style={{ marginLeft: "5px" }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);

