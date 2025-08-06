import { apiService } from "./api.service";
import { Comment } from "../types/comment";
import { authService } from "./auth.service";

const getAuthHeaders = () => {
  const token = authService.getToken();
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
};

export const commentService = {
  async getComments(taskId: number): Promise<Comment[]> {
    const response = await apiService.get(`/api/comments?task_id=${taskId}`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  },

  async addComment(comment: { task_id: number; content: string }): Promise<Comment> {
    const response = await apiService.post("/api/comments", comment, {
      headers: getAuthHeaders(),
    });
    return response.data;
  },

  async updateComment(commentId: number, content: string): Promise<Comment> {
    const response = await apiService.put(`/api/comments/${commentId}`, { content }, {
      headers: getAuthHeaders(),
    });
    return response.data;
  },

  async deleteComment(commentId: number): Promise<void> {
    await apiService.delete(`/api/comments/${commentId}`, {
      headers: getAuthHeaders(),
    });
  },
};

