import APIService from 'frontend/services/api.service';
import { ApiResponse } from 'frontend/types';
import { Task, TasksResponse, CreateTaskRequest, UpdateTaskRequest } from 'frontend/types/task';

export default class TaskService extends APIService {
  getTasks = async (accountId: string, page: number = 1, size: number = 10): Promise<ApiResponse<TasksResponse>> =>
    this.apiClient.get(`/accounts/${accountId}/tasks`, {
      params: { page, size }
    });

  getTask = async (accountId: string, taskId: string): Promise<ApiResponse<Task>> =>
    this.apiClient.get(`/accounts/${accountId}/tasks/${taskId}`);

  createTask = async (accountId: string, taskData: CreateTaskRequest): Promise<ApiResponse<Task>> =>
    this.apiClient.post(`/accounts/${accountId}/tasks`, taskData);

  updateTask = async (accountId: string, taskId: string, taskData: UpdateTaskRequest): Promise<ApiResponse<Task>> =>
    this.apiClient.patch(`/accounts/${accountId}/tasks/${taskId}`, taskData);

  deleteTask = async (accountId: string, taskId: string): Promise<ApiResponse<void>> =>
    this.apiClient.delete(`/accounts/${accountId}/tasks/${taskId}`);
}
