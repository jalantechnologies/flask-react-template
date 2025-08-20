import APIService from 'frontend/services/api.service';
import {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  TasksResponse,
  ApiResponse,
} from 'frontend/types';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

export default class TaskService extends APIService {
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

  createTask = async (
    taskData: CreateTaskRequest,
  ): Promise<ApiResponse<Task>> => {
    const accessToken = this.getAccessToken();
    const response = await this.apiClient.post<Task>(
      `/accounts/${accessToken.accountId}/tasks`,
      taskData,
      { headers: this.getAuthHeaders() },
    );
    return new ApiResponse(response.data);
  };

  getTasks = async (
    page: number = 1,
    size: number = 10,
  ): Promise<ApiResponse<TasksResponse>> => {
    const accessToken = this.getAccessToken();
    const response = await this.apiClient.get<TasksResponse>(
      `/accounts/${accessToken.accountId}/tasks?page=${page}&size=${size}`,
      { headers: this.getAuthHeaders() },
    );
    return new ApiResponse(response.data);
  };

  getTask = async (taskId: string): Promise<ApiResponse<Task>> => {
    const accessToken = this.getAccessToken();
    const response = await this.apiClient.get<Task>(
      `/accounts/${accessToken.accountId}/tasks/${taskId}`,
      { headers: this.getAuthHeaders() },
    );
    return new ApiResponse(response.data);
  };

  updateTask = async (
    taskId: string,
    taskData: UpdateTaskRequest,
  ): Promise<ApiResponse<Task>> => {
    const accessToken = this.getAccessToken();
    const response = await this.apiClient.patch<Task>(
      `/accounts/${accessToken.accountId}/tasks/${taskId}`,
      taskData,
      { headers: this.getAuthHeaders() },
    );
    return new ApiResponse(response.data);
  };

  deleteTask = async (taskId: string): Promise<ApiResponse<void>> => {
    const accessToken = this.getAccessToken();
    await this.apiClient.delete(
      `/accounts/${accessToken.accountId}/tasks/${taskId}`,
      { headers: this.getAuthHeaders() },
    );
    return new ApiResponse(undefined);
  };
}
