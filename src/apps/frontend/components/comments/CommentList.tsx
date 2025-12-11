import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Comment } from '../../types/comment';

interface CommentListProps {
  accountId: string;
  taskId: string;
  onCommentChange?: () => void;
}

const CommentList: React.FC<CommentListProps> = ({ accountId, taskId, onCommentChange }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchComments();
  }, [accountId, taskId]);

  const fetchComments = async () => {
    try {
      const response = await axios.get(`/api/v1/accounts/${accountId}/tasks/${taskId}/comments`);
      setComments(response.data.items);
    } catch (err) {
      setError('Failed to fetch comments');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (commentId: string) => {
    if (!confirm('Are you sure you want to delete this comment?')) return;

    try {
      await axios.delete(`/api/v1/accounts/${accountId}/tasks/${taskId}/comments/${commentId}`);
      fetchComments();
      onCommentChange?.();
    } catch (err) {
      setError('Failed to delete comment');
    }
  };

  if (loading) return <div>Loading comments...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h3>Comments</h3>
      {comments.length === 0 ? (
        <p>No comments yet.</p>
      ) : (
        <ul>
          {comments.map((comment) => (
            <li key={comment.id}>
              <p>{comment.content}</p>
              <small>Created at: {new Date(comment.created_at).toLocaleString()}</small>
              <button onClick={() => handleDelete(comment.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default CommentList;
