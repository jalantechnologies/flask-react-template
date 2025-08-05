import APIService from 'frontend/services/api.service';
import { Comment, AccessToken, ApiResponse } from 'frontend/types';
import { JsonObject } from 'frontend/types/common-types';

export default class CommentService extends APIService {
  createComment = async (
    userAccessToken: AccessToken,
    taskId: string,
    content: string
  ): Promise<ApiResponse<Comment>> => {
    const response = await this.apiClient.post<JsonObject>(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}/comments`,
      { content },
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      }
    );
    return new ApiResponse(new Comment(response.data));
  };

  getComment = async (
    userAccessToken: AccessToken,
    taskId: string,
    commentId: string
  ): Promise<ApiResponse<Comment>> => {
    const response = await this.apiClient.get<JsonObject>(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}/comments/${commentId}`,
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      }
    );
    return new ApiResponse(new Comment(response.data));
  };

  getPaginatedComments = async (
    userAccessToken: AccessToken,
    taskId: string,
    page?: number,
    size?: number
  ): Promise<ApiResponse<{ items: Comment[]; total_count: number; total_pages: number; pagination_params: { page: number; size: number } }>> => {
    let url = `/accounts/${userAccessToken.accountId}/tasks/${taskId}/comments`;
    
    // Add pagination parameters if provided
    const params: string[] = [];
    if (page !== undefined) params.push(`page=${page}`);
    if (size !== undefined) params.push(`size=${size}`);
    if (params.length > 0) url += `?${params.join('&')}`;
    
    const response = await this.apiClient.get<JsonObject>(url, {
      headers: {
        Authorization: `Bearer ${userAccessToken.token}`,
      },
    });
    
    // Transform the response data
    const data = response.data as JsonObject;
    const items = (data.items as JsonObject[]).map(item => new Comment(item));
    
    return new ApiResponse({
      items,
      total_count: data.total_count as number,
      total_pages: data.total_pages as number,
      pagination_params: data.pagination_params as { page: number; size: number },
    });
  };

  updateComment = async (
    userAccessToken: AccessToken,
    taskId: string,
    commentId: string,
    content: string
  ): Promise<ApiResponse<Comment>> => {
    const response = await this.apiClient.patch<JsonObject>(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}/comments/${commentId}`,
      { content },
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      }
    );
    return new ApiResponse(new Comment(response.data));
  };

  deleteComment = async (
    userAccessToken: AccessToken,
    taskId: string,
    commentId: string
  ): Promise<ApiResponse<void>> => {
    await this.apiClient.delete(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}/comments/${commentId}`,
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      }
    );
    return new ApiResponse<void>();
  };
}