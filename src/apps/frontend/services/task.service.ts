import APIService from 'frontend/services/api.service';
import { ApiResponse } from 'frontend/types';
import {
  CreateTaskRequest,
  PaginatedTasksResponse,
  Task,
  UpdateTaskRequest,
} from 'frontend/types/task';

export default class TaskService extends APIService {
  getTasks = async (
    accountId: string,
    page: number = 1,
    size: number = 10,
  ): Promise<ApiResponse<PaginatedTasksResponse>> => {
    const response = await this.apiClient.get(
      `/accounts/${accountId}/tasks?page=${page}&size=${size}`,
    );
    return new ApiResponse(response.data);
  };

  getTask = async (
    accountId: string,
    taskId: string,
  ): Promise<ApiResponse<Task>> => {
    const response = await this.apiClient.get(
      `/accounts/${accountId}/tasks/${taskId}`,
    );
    return new ApiResponse(response.data);
  };

  createTask = async (
    accountId: string,
    taskData: CreateTaskRequest,
  ): Promise<ApiResponse<Task>> => {
    const response = await this.apiClient.post(
      `/accounts/${accountId}/tasks`,
      taskData,
    );
    return new ApiResponse(response.data);
  };

  updateTask = async (
    accountId: string,
    taskId: string,
    taskData: UpdateTaskRequest,
  ): Promise<ApiResponse<Task>> => {
    const response = await this.apiClient.patch(
      `/accounts/${accountId}/tasks/${taskId}`,
      taskData,
    );
    return new ApiResponse(response.data);
  };

  deleteTask = async (
    accountId: string,
    taskId: string,
  ): Promise<ApiResponse<void>> => {
    await this.apiClient.delete(`/accounts/${accountId}/tasks/${taskId}`);
    return new ApiResponse(undefined);
  };
}
