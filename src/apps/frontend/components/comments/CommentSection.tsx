import React, { useState, useEffect } from "react";
import axios from "axios";

interface Comment {
  id: string;
  task_id: string;
  author: string;
  content: string;
  created_at: string;
}

interface Props {
  taskId: string;
}

const CommentSection: React.FC<Props> = ({ taskId }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [author, setAuthor] = useState("");
  const [content, setContent] = useState("");

  const fetchComments = async () => {
    try {
      const res = await axios.get<Comment[]>(`http://localhost:5000/comments/task/${taskId}`);
      setComments(res.data);
    } catch (error) {
      console.error("Error fetching comments:", error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!author || !content) return;

    try {
      await axios.post("http://localhost:5000/comments", {
        task_id: taskId,
        author,
        content,
      });
      setAuthor("");
      setContent("");
      fetchComments();
    } catch (error) {
      console.error("Error posting comment:", error);
    }
  };

  useEffect(() => {
    fetchComments();
  }, [taskId]);

  return (
    <div className="p-4 bg-gray-800 rounded text-white">
      <h2 className="text-xl font-bold mb-4">Comments</h2>

      <form onSubmit={handleSubmit} className="space-y-2 mb-4">
        <input
          type="text"
          placeholder="Your name"
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          className="w-full p-2 bg-gray-700 rounded"
        />
        <textarea
          placeholder="Write a comment..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full p-2 bg-gray-700 rounded"
        />
        <button type="submit" className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-500">
          Post
        </button>
      </form>

      <div className="space-y-4">
        {comments.map((comment) => (
          <div key={comment.id} className="border-b border-gray-600 pb-2">
            <p className="font-semibold">{comment.author}</p>
            <p>{comment.content}</p>
            <p className="text-sm text-gray-400">{new Date(comment.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CommentSection;
