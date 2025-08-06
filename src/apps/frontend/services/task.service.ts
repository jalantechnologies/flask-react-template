import APIService from 'frontend/services/api.service';
import {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  TaskListResponse,
  AccessToken,
  ApiResponse,
} from 'frontend/types';

export default class TaskService extends APIService {
  getTasks = async (
    userAccessToken: AccessToken,
    page: number = 1,
    perPage: number = 10,
  ): Promise<ApiResponse<TaskListResponse>> =>
    this.apiClient.get(`/accounts/${userAccessToken.accountId}/tasks`, {
      headers: {
        Authorization: `Bearer ${userAccessToken.token}`,
      },
      params: {
        page,
        per_page: perPage,
      },
    });

  getTask = async (
    userAccessToken: AccessToken,
    taskId: string,
  ): Promise<ApiResponse<Task>> =>
    this.apiClient.get(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      },
    );

  createTask = async (
    userAccessToken: AccessToken,
    taskData: CreateTaskRequest,
  ): Promise<ApiResponse<Task>> =>
    this.apiClient.post(
      `/accounts/${userAccessToken.accountId}/tasks`,
      taskData,
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      },
    );

  updateTask = async (
    userAccessToken: AccessToken,
    taskId: string,
    taskData: UpdateTaskRequest,
  ): Promise<ApiResponse<Task>> =>
    this.apiClient.patch(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}`,
      taskData,
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      },
    );

  deleteTask = async (
    userAccessToken: AccessToken,
    taskId: string,
  ): Promise<
    ApiResponse<{ task_id: string; deleted_at: string; success: boolean }>
  > =>
    this.apiClient.delete(
      `/accounts/${userAccessToken.accountId}/tasks/${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${userAccessToken.token}`,
        },
      },
    );
}
