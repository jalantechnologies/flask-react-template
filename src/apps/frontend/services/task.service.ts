import APIService from 'frontend/services/api.service';
import {
  ApiResponse,
  Task,
  PaginationParams,
} from 'frontend/types';

export default class TaskService extends APIService {
  /**
   * Get all tasks for an account with pagination
   */
  getTasks = async (
    accountId: string,
    paginationParams?: PaginationParams,
  ): Promise<ApiResponse<{ items: Task[], totalCount: number, totalPages: number, paginationParams: any }>> => {
    const params = paginationParams || new PaginationParams();
    const response = await this.apiClient.get(
      `/accounts/${accountId}/tasks?page=${params.page}&size=${params.size}`,
    );
    return new ApiResponse(response.data);
  };

  /**
   * Get a single task by ID
   */
  getTask = async (
    accountId: string,
    taskId: string,
  ): Promise<ApiResponse<Task>> => {
    const response = await this.apiClient.get(
      `/accounts/${accountId}/tasks/${taskId}`,
    );
    return new ApiResponse(new Task(response.data));
  };

  /**
   * Create a new task
   */
  createTask = async (
    accountId: string,
    title: string,
    description: string,
  ): Promise<ApiResponse<Task>> => {
    const response = await this.apiClient.post(
      `/accounts/${accountId}/tasks`,
      {
        title,
        description,
      },
    );
    return new ApiResponse(new Task(response.data));
  };

  /**
   * Update an existing task
   */
  updateTask = async (
    accountId: string,
    taskId: string,
    title: string,
    description: string,
  ): Promise<ApiResponse<Task>> => {
    const response = await this.apiClient.patch(
      `/accounts/${accountId}/tasks/${taskId}`,
      {
        title,
        description,
      },
    );
    return new ApiResponse(new Task(response.data));
  };

  /**
   * Delete a task
   */
  deleteTask = async (
    accountId: string,
    taskId: string,
  ): Promise<ApiResponse<void>> => {
    await this.apiClient.delete(
      `/accounts/${accountId}/tasks/${taskId}`,
    );
    return new ApiResponse();
  };
}