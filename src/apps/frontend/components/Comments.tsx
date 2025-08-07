import React, { useState, useEffect, FC } from 'react';
import './Comments.css';

interface Comment {
  id: string;
  author_id: string;
  text: string;
  created_at: string;
}

interface CommentsProps {
  taskId: string;
}

const Comments: FC<CommentsProps> = ({ taskId }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newCommentText, setNewCommentText] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const fetchComments = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/comments/for-task/${taskId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch comments.');
      }
      const data: Comment[] = await response.json();
      setComments(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePostComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCommentText.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:5000/api/comments/for-task/${taskId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          author_id: 'frontend-user',
          text: newCommentText,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to post comment.');
      }

      const newComment: Comment = await response.json();
      setComments([...comments, newComment]);
      setNewCommentText('');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleDeleteComment = async (commentId: string) => {
    setError(null);

    try {
      await fetch(`http://localhost:5000/api/comments/${commentId}`, {
        method: 'DELETE',
      });
      setComments(comments.filter(c => c.id !== commentId));
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchComments();
  }, [taskId]);

  return (
    <div className="comments-container">
      <h2>Comments</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {isLoading ? (
        <p>Loading comments...</p>
      ) : (
        <ul className="comments-list">
          {comments.map((comment) => (
            <li key={comment.id} className="comment-item">
              <p>
                <strong className="comment-author">{comment.author_id}</strong>: {comment.text}
              </p>
              <button onClick={() => handleDeleteComment(comment.id)} className="delete-button">
                &times;
              </button>
            </li>
          ))}
        </ul>
      )}

      <form className="comment-form" onSubmit={handlePostComment}>
        <input
          type="text"
          value={newCommentText}
          onChange={(e) => setNewCommentText(e.target.value)}
          placeholder="Write a new comment..."
          disabled={isSubmitting}
        />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting...' : 'Submit'}
        </button>
      </form>
    </div>
  );
};

export default Comments;