import { useEffect, useState } from 'react';
import CommentForm from './CommentForm';

export default function CommentList() {
  const [comments, setComments] = useState([]);
  const [editing, setEditing] = useState(null);

  const fetchComments = async () => {
    const res = await fetch('/comments/');
    const data = await res.json();
    setComments(data);
  };

  useEffect(() => {
    fetchComments();
  }, []);

  const addComment = async (comment) => {
    await fetch('/comments/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(comment),
    });
    fetchComments();
  };

  const updateComment = async (comment) => {
    await fetch(`/comments/${editing.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(comment),
    });
    setEditing(null);
    fetchComments();
  };

  const deleteComment = async (id) => {
    await fetch(`/comments/${id}`, { method: 'DELETE' });
    fetchComments();
  };

  return (
    <div>
      <h2>{editing ? 'Edit' : 'Add'} Comment</h2>
      <CommentForm
        onSubmit={editing ? updateComment : addComment}
        initialData={editing}
      />
      <h2>All Comments</h2>
      <ul>
        {comments.map((c) => (
          <li key={c.id}>
            Task #{c.task_id}: {c.content}
            <button onClick={() => setEditing(c)}>Edit</button>
            <button onClick={() => deleteComment(c.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
