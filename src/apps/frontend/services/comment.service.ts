import APIService from 'frontend/services/api.service';
import {
  ApiResponse,
  Comment,
  CommentListResponse,
  CommentDeletionResult,
  CreateCommentRequest,
  UpdateCommentRequest,
  PaginationParams,
} from 'frontend/types';

export default class CommentService extends APIService {
  /**
   * Create a new comment for a task
   */
  createComment = async (
    accountId: string,
    taskId: string,
    content: string,
  ): Promise<ApiResponse<Comment>> => {
    const request = new CreateCommentRequest(content);
    const response = await this.apiClient.post(
      `/accounts/${accountId}/tasks/${taskId}/comments`,
      request.toJson(),
    );
    return new ApiResponse(new Comment(response.data));
  };

  /**
   * Get all comments for a task with pagination
   */
  getComments = async (
    accountId: string,
    taskId: string,
    paginationParams?: PaginationParams,
  ): Promise<ApiResponse<CommentListResponse>> => {
    const params = paginationParams || new PaginationParams();
    const response = await this.apiClient.get(
      `/accounts/${accountId}/tasks/${taskId}/comments?page=${params.page}&size=${params.size}`,
    );
    return new ApiResponse(new CommentListResponse(response.data));
  };

  /**
   * Get a single comment by ID
   */
  getComment = async (
    accountId: string,
    taskId: string,
    commentId: string,
  ): Promise<ApiResponse<Comment>> => {
    const response = await this.apiClient.get(
      `/accounts/${accountId}/tasks/${taskId}/comments/${commentId}`,
    );
    return new ApiResponse(new Comment(response.data));
  };

  /**
   * Update an existing comment
   */
  updateComment = async (
    accountId: string,
    taskId: string,
    commentId: string,
    content: string,
  ): Promise<ApiResponse<Comment>> => {
    const request = new UpdateCommentRequest(content);
    const response = await this.apiClient.patch(
      `/accounts/${accountId}/tasks/${taskId}/comments/${commentId}`,
      request.toJson(),
    );
    return new ApiResponse(new Comment(response.data));
  };

  /**
   * Delete a comment
   */
  deleteComment = async (
    accountId: string,
    taskId: string,
    commentId: string,
  ): Promise<ApiResponse<CommentDeletionResult>> => {
    const response = await this.apiClient.delete(
      `/accounts/${accountId}/tasks/${taskId}/comments/${commentId}`,
    );
    return new ApiResponse(new CommentDeletionResult(response.data));
  };
}