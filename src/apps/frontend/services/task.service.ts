import { AxiosResponse } from 'axios';

import APIService from 'frontend/services/api.service';
import { TaskModel } from 'frontend/types/task';
import { JsonObject } from 'frontend/types/common-types';

export default class TaskService extends APIService {
  private getAuthHeaders() {
    const token = localStorage.getItem('accessToken');
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    };
  }

  async getTasks(accountId: string, filters?: { page?: number; size?: number }): Promise<{
    items: TaskModel[];
    totalCount: number;
    page: number;
    size: number;
  }> {
    const params = new URLSearchParams();
    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.size) params.append('size', filters.size.toString());

    const response: AxiosResponse<JsonObject> = await this.apiClient.get(
      `/accounts/${accountId}/tasks${params.toString() ? `?${params.toString()}` : ''}`,
      { headers: this.getAuthHeaders() }
    );

    const data = response.data as JsonObject;
    const items = (data.items as JsonObject[]).map((item) => TaskModel.fromJson(item));
    const totalCount = data.total_count as number;
    const page = (data.pagination_params as JsonObject).page as number;
    const size = (data.pagination_params as JsonObject).size as number;

    return { items, totalCount, page, size };
  }

  async getTask(accountId: string, taskId: string): Promise<TaskModel> {
    const response: AxiosResponse<JsonObject> = await this.apiClient.get(
      `/accounts/${accountId}/tasks/${taskId}`,
      { headers: this.getAuthHeaders() }
    );

    return TaskModel.fromJson(response.data);
  }

  async createTask(accountId: string, taskData: { title: string; description: string }): Promise<TaskModel> {
    const response: AxiosResponse<JsonObject> = await this.apiClient.post(
      `/accounts/${accountId}/tasks`,
      taskData,
      { headers: this.getAuthHeaders() }
    );

    return TaskModel.fromJson(response.data);
  }

  async updateTask(
    accountId: string,
    taskId: string,
    taskData: { title: string; description: string }
  ): Promise<TaskModel> {
    const response: AxiosResponse<JsonObject> = await this.apiClient.patch(
      `/accounts/${accountId}/tasks/${taskId}`,
      taskData,
      { headers: this.getAuthHeaders() }
    );

    return TaskModel.fromJson(response.data);
  }

  async deleteTask(accountId: string, taskId: string): Promise<void> {
    await this.apiClient.delete(`/accounts/${accountId}/tasks/${taskId}`, {
      headers: this.getAuthHeaders(),
    });
  }
} 