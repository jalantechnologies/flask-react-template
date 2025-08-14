import APIService from 'frontend/services/api.service';
import { ApiResponse } from 'frontend/types';
import {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  PaginatedTasksResponse,
} from 'frontend/types/task';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

export default class TaskService extends APIService {
  _getAccessToken = () => {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) throw new Error('Access token not found');
    return accessToken;
  };

  // Get paginated tasks for an account
  getTasks = async (
    page: number = 1,
    size: number = 10,
  ): Promise<ApiResponse<PaginatedTasksResponse>> => {
    const accessToken = this._getAccessToken();
    return this.apiClient.get(`/accounts/${accessToken.accountId}/tasks`, {
      headers: {
        Authorization: `Bearer ${accessToken.token}`,
      },
      params: { page, size },
    });
  };

  // Get a single task by ID
  getTask = async (taskId: string): Promise<ApiResponse<Task>> => {
    const accessToken = this._getAccessToken();
    return this.apiClient.get(
      `/accounts/${accessToken.accountId}/tasks/${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken.token}`,
        },
      },
    );
  };

  // Create a new task
  createTask = async (
    taskData: CreateTaskRequest,
  ): Promise<ApiResponse<Task>> => {
    const accessToken = this._getAccessToken();
    return this.apiClient.post(
      `/accounts/${accessToken.accountId}/tasks`,
      taskData,
      {
        headers: {
          Authorization: `Bearer ${accessToken.token}`,
        },
      },
    );
  };

  // Update an existing task
  updateTask = async (
    taskId: string,
    taskData: UpdateTaskRequest,
  ): Promise<ApiResponse<Task>> => {
    const accessToken = this._getAccessToken();
    return this.apiClient.patch(
      `/accounts/${accessToken.accountId}/tasks/${taskId}`,
      taskData,
      {
        headers: {
          Authorization: `Bearer ${accessToken.token}`,
        },
      },
    );
  };

  // Delete a task
  deleteTask = async (taskId: string): Promise<ApiResponse<void>> => {
    const accessToken = this._getAccessToken();
    return this.apiClient.delete(
      `/accounts/${accessToken.accountId}/tasks/${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken.token}`,
        },
      },
    );
  };
}
