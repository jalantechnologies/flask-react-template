import React, { useEffect, useState } from "react";

type Comment = {
  id: number;
  content: string;
  created_at?: string;
};

type CommentSectionProps = {
  taskId: number;
};

const CommentSection: React.FC<CommentSectionProps> = ({ taskId }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newContent, setNewContent] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState("");

  useEffect(() => {
    fetch(`/tasks/${taskId}/comments/`)
      .then((res) => res.json())
      .then((data: Comment[]) => setComments(data))
      .catch((err) => console.error("Error fetching comments", err));
  }, [taskId]);

  const handleAddComment = async () => {
    if (!newContent.trim()) return;

    const response = await fetch(`/tasks/${taskId}/comments/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: newContent }),
    });

    const data: Comment = await response.json();
    setComments((prev) => [...prev, data]);
    setNewContent("");
  };

  const handleDelete = async (id: number) => {
    await fetch(`/comments/${id}/`, { method: "DELETE" });
    setComments((prev) => prev.filter((c) => c.id !== id));
  };

  const handleUpdate = async () => {
    if (editingId === null) return;

    const response = await fetch(`/comments/${editingId}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: editingContent }),
    });

    const updated: Comment = await response.json();
    setComments((prev) =>
      prev.map((c) => (c.id === editingId ? updated : c))
    );
    setEditingId(null);
    setEditingContent("");
  };

  return (
    <div style={{ borderTop: "1px solid #ccc", marginTop: "2rem", paddingTop: "1rem" }}>
      <h3>Comments</h3>

      {comments.length === 0 && <p>No comments yet.</p>}

      {comments.map((comment) => (
        <div key={comment.id} style={{ marginBottom: "1rem" }}>
          {editingId === comment.id ? (
            <>
              <input
                value={editingContent}
                onChange={(e) => setEditingContent(e.target.value)}
                placeholder="Edit comment"
              />
              <button onClick={handleUpdate}>Save</button>
              <button onClick={() => setEditingId(null)}>Cancel</button>
            </>
          ) : (
            <>
              <span>{comment.content}</span>
              <button onClick={() => {
                setEditingId(comment.id);
                setEditingContent(comment.content);
              }}>Edit</button>
              <button onClick={() => handleDelete(comment.id)}>Delete</button>
            </>
          )}
        </div>
      ))}

      <div style={{ marginTop: "1rem" }}>
        <input
          value={newContent}
          onChange={(e) => setNewContent(e.target.value)}
          placeholder="Add a comment"
        />
        <button onClick={handleAddComment}>Add</button>
      </div>
    </div>
  );
};

export default CommentSection;
