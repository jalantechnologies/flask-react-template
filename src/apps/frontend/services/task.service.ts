import APIService from 'frontend/services/api.service';
import { 
  AccessToken, 
  ApiResponse,
  Task, 
  CreateTaskRequest, 
  UpdateTaskRequest, 
  TasksListResponse,
  PaginationParams 
} from 'frontend/types';

export default class TaskService extends APIService {
  /**
   * Get all tasks for the current user's account
   */
  getTasks = async (
    userAccessToken: AccessToken,
    pagination?: PaginationParams
  ): Promise<ApiResponse<TasksListResponse>> => {
    const queryParams = new URLSearchParams();
    if (pagination?.page) {
      queryParams.append('page', pagination.page.toString());
    }
    if (pagination?.size) {
      queryParams.append('size', pagination.size.toString());
    }
    
    const url = `/accounts/${userAccessToken.accountId}/tasks${
      queryParams.toString() ? `?${queryParams.toString()}` : ''
    }`;

    return this.apiClient.get(url, {
      headers: {
        Authorization: `Bearer ${userAccessToken.token}`,
      },
    });
  };

  /**
   * Get a specific task by ID
   */
  getTask = async (
    userAccessToken: AccessToken,
    taskId: string
  ): Promise<ApiResponse<Task>> =>
    this.apiClient.get(`/accounts/${userAccessToken.accountId}/tasks/${taskId}`, {
      headers: {
        Authorization: `Bearer ${userAccessToken.token}`,
      },
    });

  /**
   * Create a new task
   */
  createTask = async (
    userAccessToken: AccessToken,
    taskData: CreateTaskRequest
  ): Promise<ApiResponse<Task>> =>
    this.apiClient.post(
      `/accounts/${userAccessToken.accountId}/tasks`,
      taskData,
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
          'Content-Type': 'application/json',
        },
      }
    );

  /**
   * Update an existing task
   */
  updateTask = async (
    userAccessToken: AccessToken,
    taskId: string,
    taskData: UpdateTaskRequest
  ): Promise<ApiResponse<Task>> =>
    this.apiClient.patch(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}`,
      taskData,
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
          'Content-Type': 'application/json',
        },
      }
    );

  /**
   * Delete a task
   */
  deleteTask = async (
    userAccessToken: AccessToken,
    taskId: string
  ): Promise<ApiResponse<void>> =>
    this.apiClient.delete(`/accounts/${userAccessToken.accountId}/tasks/${taskId}`, {
      headers: {
        Authorization: `Bearer ${userAccessToken.token}`,
      },
    });
}