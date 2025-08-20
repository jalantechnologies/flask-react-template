import APIService from 'frontend/services/api.service';
import {
  Comment,
  CreateCommentRequest,
  UpdateCommentRequest,
  CommentsResponse,
  ApiResponse,
} from 'frontend/types';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

export default class CommentService extends APIService {
  private getAccessToken() {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) {
      throw new Error('No access token found');
    }
    return accessToken;
  }

  private getAuthHeaders() {
    const accessToken = this.getAccessToken();
    return {
      Authorization: `Bearer ${accessToken.token}`,
    };
  }

  createComment = async (
    taskId: string,
    commentData: CreateCommentRequest,
  ): Promise<ApiResponse<Comment>> => {
    const accessToken = this.getAccessToken();
    const response = await this.apiClient.post<Comment>(
      `/accounts/${accessToken.accountId}/tasks/${taskId}/comments`,
      commentData,
      { headers: this.getAuthHeaders() },
    );
    return new ApiResponse(response.data);
  };

  getComments = async (
    taskId: string,
    page: number = 1,
    size: number = 10,
  ): Promise<ApiResponse<CommentsResponse>> => {
    const accessToken = this.getAccessToken();
    const response = await this.apiClient.get<CommentsResponse>(
      `/accounts/${accessToken.accountId}/tasks/${taskId}/comments?page=${page}&size=${size}`,
      { headers: this.getAuthHeaders() },
    );
    return new ApiResponse(response.data);
  };

  getComment = async (
    taskId: string,
    commentId: string,
  ): Promise<ApiResponse<Comment>> => {
    const accessToken = this.getAccessToken();
    const response = await this.apiClient.get<Comment>(
      `/accounts/${accessToken.accountId}/tasks/${taskId}/comments/${commentId}`,
      { headers: this.getAuthHeaders() },
    );
    return new ApiResponse(response.data);
  };

  updateComment = async (
    taskId: string,
    commentId: string,
    commentData: UpdateCommentRequest,
  ): Promise<ApiResponse<Comment>> => {
    const accessToken = this.getAccessToken();
    const response = await this.apiClient.patch<Comment>(
      `/accounts/${accessToken.accountId}/tasks/${taskId}/comments/${commentId}`,
      commentData,
      { headers: this.getAuthHeaders() },
    );
    return new ApiResponse(response.data);
  };

  deleteComment = async (
    taskId: string,
    commentId: string,
  ): Promise<ApiResponse<void>> => {
    const accessToken = this.getAccessToken();
    await this.apiClient.delete(
      `/accounts/${accessToken.accountId}/tasks/${taskId}/comments/${commentId}`,
      { headers: this.getAuthHeaders() },
    );
    return new ApiResponse(undefined);
  };
}
