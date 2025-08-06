import { useState, useEffect } from 'react';

export default function CommentForm({ onSubmit, initialData }) {
  const [task_id, setTaskId] = useState(initialData?.task_id || '');
  const [content, setContent] = useState(initialData?.content || '');

  useEffect(() => {
    setTaskId(initialData?.task_id || '');
    setContent(initialData?.content || '');
  }, [initialData]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ task_id, content });
    setTaskId('');
    setContent('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="number"
        placeholder="Task ID"
        value={task_id}
        onChange={(e) => setTaskId(e.target.value)}
        required
      />
      <input
        type="text"
        placeholder="Comment Content"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        required
      />
      <button type="submit">{initialData ? 'Update' : 'Add'} Comment</button>
    </form>
  );
}
