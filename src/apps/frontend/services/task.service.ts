import APIService from 'frontend/services/api.service';
import { AccessToken, ApiResponse, Task } from 'frontend/types';
import { JsonObject } from 'frontend/types/common-types';

export default class TaskService extends APIService {
  createTask = async (
    userAccessToken: AccessToken,
    title: string,
    description: string
  ): Promise<ApiResponse<Task>> => {
    const response = await this.apiClient.post<JsonObject>(
      `/accounts/${userAccessToken.accountId}/tasks`,
      { title, description },
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      }
    );
    return new ApiResponse(response.data as Task);
  };

  getTask = async (
    userAccessToken: AccessToken,
    taskId: string
  ): Promise<ApiResponse<Task>> => {
    const response = await this.apiClient.get<JsonObject>(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      }
    );
    return new ApiResponse(response.data as Task);
  };

  getPaginatedTasks = async (
    userAccessToken: AccessToken,
    page?: number,
    size?: number
  ): Promise<ApiResponse<{ items: Task[]; total_count: number; total_pages: number; pagination_params: { page: number; size: number } }>> => {
    let url = `/accounts/${userAccessToken.accountId}/tasks`;
    
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
    
    return new ApiResponse(response.data as { 
      items: Task[]; 
      total_count: number; 
      total_pages: number; 
      pagination_params: { page: number; size: number } 
    });
  };

  updateTask = async (
    userAccessToken: AccessToken,
    taskId: string,
    title: string,
    description: string
  ): Promise<ApiResponse<Task>> => {
    const response = await this.apiClient.patch<JsonObject>(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}`,
      { title, description },
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      }
    );
    return new ApiResponse(response.data as Task);
  };

  deleteTask = async (
    userAccessToken: AccessToken,
    taskId: string
  ): Promise<ApiResponse<void>> => {
    await this.apiClient.delete(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      }
    );
    return new ApiResponse<void>();
  };
}