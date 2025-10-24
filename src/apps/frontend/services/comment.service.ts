import ApiService from './api.service';
import {
  Comment,
  CreateCommentDto,
  UpdateCommentDto,
} from 'frontend/types/comments';

class CommentService extends ApiService {
  async getAllComments(accountId: string, taskId: string): Promise<Comment[]> {
    const response = await this.apiClient.get<Comment[]>(
      `/accounts/${accountId}/tasks/${taskId}/comments`,
    );
    return response.data;
  }

  async createComment(
    accountId: string,
    taskId: string,
    dto: CreateCommentDto,
  ): Promise<Comment> {
    const response = await this.apiClient.post<Comment>(
      `/accounts/${accountId}/tasks/${taskId}/comments`,
      dto,
    );
    return response.data;
  }

  async updateComment(
    accountId: string,
    taskId: string,
    commentId: string,
    dto: UpdateCommentDto,
  ): Promise<Comment> {
    const response = await this.apiClient.put<Comment>(
      `/accounts/${accountId}/tasks/${taskId}/comments/${commentId}`,
      dto,
    );
    return response.data;
  }

  async deleteComment(
    accountId: string,
    taskId: string,
    commentId: string,
  ): Promise<void> {
    await this.apiClient.delete(
      `/accounts/${accountId}/tasks/${taskId}/comments/${commentId}`,
    );
  }
}

export default new CommentService();
