import React, { useEffect, useState } from "react";

function App() {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [editCommentId, setEditCommentId] = useState(null);
  const [editContent, setEditContent] = useState("");
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    fetchComments();
  }, []);

  const fetchComments = () => {
    fetch("http://localhost:5000/comments")
      .then((res) => res.json())
      .then((data) => setComments(data))
      .catch((err) => console.error("Fetch error:", err));
  };

  const handleAddComment = () => {
    if (!newComment.trim()) return;

    fetch("http://localhost:5000/comments", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ comment: newComment }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to add comment");
        return res.json();
      })
      .then(() => {
        fetchComments();
        setNewComment("");
      })
      .catch((err) => console.error("Add error:", err));
  };

  const handleDeleteComment = (id) => {
    fetch(`http://localhost:5000/comments/${id}`, {
      method: "DELETE",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to delete comment");
        fetchComments();
      })
      .catch((err) => console.error("Delete error:", err));
  };

  const handleEditClick = (id, currentContent) => {
    setEditCommentId(id);
    setEditContent(currentContent);
  };

  const handleCancelEdit = () => {
    setEditCommentId(null);
    setEditContent("");
  };

  const handleSaveEdit = (id) => {
    if (!editContent.trim()) return;

    fetch(`http://localhost:5000/comments/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ comment: editContent }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to update comment");
        return res.json();
      })
      .then(() => {
        fetchComments();
        setEditCommentId(null);
        setEditContent("");
      })
      .catch((err) => console.error("Edit error:", err));
  };

  const theme = darkMode ? dark : light;

  return (
    <div style={{ ...styles.container, background: theme.background, color: theme.text }}>
      <h1 style={styles.title}>💬 Comments</h1>

      <div style={styles.toggleContainer}>
        <button onClick={() => setDarkMode(!darkMode)} style={styles.toggleButton}>
          {darkMode ? "🌞 Light Mode" : "🌙 Dark Mode"}
        </button>
      </div>

      <div style={styles.inputContainer}>
        <input
          type="text"
          value={newComment}
          placeholder="Write a comment..."
          onChange={(e) => setNewComment(e.target.value)}
          style={{ ...styles.input, background: theme.inputBg, color: theme.text }}
        />
        <button onClick={handleAddComment} style={{ ...styles.addButton }}>
          ➕ Add
        </button>
      </div>

      <div style={{ marginTop: "2rem" }}>
        {comments.length === 0 ? (
          <p style={styles.noComments}>No comments yet 💤</p>
        ) : (
          <ul style={styles.list}>
            {comments.map((comment) => (
              <li
                key={comment.id}
                style={{
                  ...styles.commentBox,
                  background: theme.card,
                  color: theme.text,
                  transition: "all 0.3s ease-in-out",
                }}
              >
                {editCommentId === comment.id ? (
                  <>
                    <input
                      type="text"
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      style={{ ...styles.editInput, background: theme.inputBg, color: theme.text }}
                    />
                    <button onClick={() => handleSaveEdit(comment.id)} style={styles.saveButton}>
                      💾 Save
                    </button>
                    <button onClick={handleCancelEdit} style={styles.cancelButton}>
                      ✖ Cancel
                    </button>
                  </>
                ) : (
                  <>
                    <span style={styles.commentText}>{comment.content}</span>
                    <div style={styles.buttonGroup}>
                      <button
                        onClick={() => handleEditClick(comment.id, comment.content)}
                        style={styles.editButton}
                      >
                        ✏️ Edit
                      </button>
                      <button onClick={() => handleDeleteComment(comment.id)} style={styles.deleteButton}>
                        ❌ Delete
                      </button>
                    </div>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

// 🔥 Light & Dark Themes
const light = {
  background: "#f0f0f0",
  card: "#ffffff",
  inputBg: "#ffffff",
  text: "#222",
};

const dark = {
  background: "#1e1e1e",
  card: "#2c2c2c",
  inputBg: "#333333",
  text: "#f5f5f5",
};

// 💅 Centralized Styles
const styles = {
  container: {
    maxWidth: "600px",
    margin: "auto",
    padding: "2rem",
    minHeight: "100vh",
    transition: "background 0.3s ease, color 0.3s ease",
    fontFamily: "Segoe UI, sans-serif",
  },
  title: {
    textAlign: "center",
    fontWeight: "bold",
  },
  toggleContainer: {
    textAlign: "right",
    marginBottom: "1rem",
  },
  toggleButton: {
    padding: "0.4rem 0.8rem",
    background: "#444",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "14px",
  },
  inputContainer: {
    display: "flex",
    gap: "1rem",
    marginBottom: "1rem",
  },
  input: {
    flex: 1,
    padding: "0.5rem",
    border: "1px solid #ccc",
    borderRadius: "6px",
    fontSize: "16px",
    transition: "background 0.3s ease, color 0.3s ease",
  },
  addButton: {
    padding: "0.5rem 1rem",
    backgroundColor: "#007bff",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "bold",
  },
  list: {
    listStyle: "none",
    padding: 0,
  },
  commentBox: {
    padding: "1rem",
    marginBottom: "1rem",
    borderRadius: "8px",
    border: "1px solid #ddd",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
  },
  commentText: {
    fontSize: "16px",
    flex: 1,
  },
  buttonGroup: {
    display: "flex",
    gap: "0.5rem",
    marginLeft: "1rem",
  },
  editButton: {
    backgroundColor: "#ffc107",
    color: "white",
    border: "none",
    padding: "0.4rem 0.8rem",
    borderRadius: "4px",
    cursor: "pointer",
  },
  deleteButton: {
    backgroundColor: "#dc3545",
    color: "white",
    border: "none",
    padding: "0.4rem 0.8rem",
    borderRadius: "4px",
    cursor: "pointer",
  },
  editInput: {
    flex: 1,
    padding: "0.4rem",
    borderRadius: "4px",
    border: "1px solid #ccc",
    marginRight: "0.5rem",
  },
  saveButton: {
    backgroundColor: "green",
    color: "white",
    border: "none",
    padding: "0.4rem 0.8rem",
    borderRadius: "4px",
    cursor: "pointer",
    marginRight: "0.5rem",
  },
  cancelButton: {
    backgroundColor: "#6c757d",
    color: "white",
    border: "none",
    padding: "0.4rem 0.8rem",
    borderRadius: "4px",
    cursor: "pointer",
  },
  noComments: {
    textAlign: "center",
    color: "#888",
    fontStyle: "italic",
  },
};

export default App;
