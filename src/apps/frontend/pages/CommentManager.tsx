import React, { useState, useEffect } from 'react';

const API = 'http://localhost:5000/comments';

export default function CommentManager() {
  const [comments, setComments] = useState([]);
  const [taskId, setTaskId] = useState('');
  const [content, setContent] = useState('');
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    fetchComments();
  }, []);

  const fetchComments = async () => {
    const res = await fetch(API);
    const data = await res.json();
    setComments(data);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const method = editingId ? 'PUT' : 'POST';
    const url = editingId ? `${API}/${editingId}` : API;
    const body = editingId ? { content } : { task_id: parseInt(taskId), content };

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (res.ok) {
      setTaskId('');
      setContent('');
      setEditingId(null);
      fetchComments();
    }
  };

  const handleEdit = (comment) => {
    setEditingId(comment.id);
    setContent(comment.content);
  };

  const handleDelete = async (id) => {
    const res = await fetch(`${API}/${id}`, { method: 'DELETE' });
    if (res.ok) fetchComments();
  };

  return (
    <div>
      <h2>Comment Manager</h2>
      <form onSubmit={handleSubmit}>
        {!editingId && (
          <input
            type="number"
            placeholder="Task ID"
            value={taskId}
            onChange={(e) => setTaskId(e.target.value)}
            required
          />
        )}
        <input
          type="text"
          placeholder="Comment"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />
        <button type="submit">{editingId ? 'Update' : 'Add'}</button>
      </form>

      <ul>
        {comments.map((comment) => (
          <li key={comment.id}>
            Task #{comment.task_id}: {comment.content}{' '}
            <button onClick={() => handleEdit(comment)}>Edit</button>
            <button onClick={() => handleDelete(comment.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
