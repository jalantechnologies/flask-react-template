import React, { useEffect, useState } from "react";
import { commentService } from "../../services/comment.service";
import { Comment } from "../../types/comment";

interface CommentSectionProps {
  taskId: number;
}

export const CommentSection: React.FC<CommentSectionProps> = ({ taskId }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [newComment, setNewComment] = useState<string>("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState<string>("");

  const fetchComments = async () => {
    setLoading(true);
    try {
      const data = await commentService.getComments(taskId);
      setComments(data);
    } catch (error) {
      console.error("Error loading comments:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComments();
  }, [taskId]);

  const handleAddComment = async () => {
    if (!newComment.trim()) return;
    try {
      await commentService.addComment({ task_id: taskId, content: newComment });
      setNewComment("");
      fetchComments();
    } catch (error) {
      console.error("Error adding comment:", error);
    }
  };

  const handleUpdateComment = async (id: number) => {
    if (!editingContent.trim()) return;
    try {
      await commentService.updateComment(id, editingContent);
      setEditingId(null);
      setEditingContent("");
      fetchComments();
    } catch (error) {
      console.error("Error updating comment:", error);
    }
  };

  const handleDeleteComment = async (id: number) => {
    if (!window.confirm("Delete this comment?")) return;
    try {
      await commentService.deleteComment(id);
      fetchComments();
    } catch (error) {
      console.error("Error deleting comment:", error);
    }
  };

  return (
    <div>
      <h3>Comments</h3>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul>
          {comments.map((comment) => (
            <li key={comment.id} style={{ marginBottom: "10px" }}>
              {editingId === comment.id ? (
                <>
                  <input
                    type="text"
                    value={editingContent}
                    onChange={(e) => setEditingContent(e.target.value)}
                  />
                  <button onClick={() => handleUpdateComment(comment.id)}>Save</button>
                  <button onClick={() => setEditingId(null)}>Cancel</button>
                </>
              ) : (
                <>
                  <span>{comment.content}</span>
                  <button onClick={() => {
                    setEditingId(comment.id);
                    setEditingContent(comment.content);
                  }}>Edit</button>
                  <button onClick={() => handleDeleteComment(comment.id)}>Delete</button>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
      <div style={{ marginTop: "10px" }}>
        <input
          type="text"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Write a comment"
        />
        <button onClick={handleAddComment}>Add Comment</button>
      </div>
    </div>
  );
};

