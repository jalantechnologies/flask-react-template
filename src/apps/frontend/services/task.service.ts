import APIService from 'frontend/services/api.service';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

export interface Task {
  id: string;
  account_id: string;
  title: string;
  description: string;
  created_at?: string;
  updated_at?: string;
}

export interface Comment {
  id: string;
  task_id: string;
  account_id: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  title: string;
  description: string;
}

export interface UpdateTaskRequest {
  title: string;
  description: string;
}

export interface CreateCommentRequest {
  content: string;
}

export interface UpdateCommentRequest {
  content: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

export default class TaskService extends APIService {
  private static getAuthHeaders() {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) {
      throw new Error('Access token not found');
    }
    return {
      Authorization: `Bearer ${accessToken.token}`,
    };
  }

  // Task APIs
  async createTask(accountId: string, data: CreateTaskRequest): Promise<Task> {
    const response = await this.apiClient.post(
      `/accounts/${accountId}/tasks`,
      data,
      {
        headers: TaskService.getAuthHeaders(),
      },
    );
    return response.data as Task;
  }

  async getTasks(
    accountId: string,
    page: number = 1,
    size: number = 10,
  ): Promise<PaginatedResponse<Task>> {
    const response = await this.apiClient.get(`/accounts/${accountId}/tasks`, {
      params: { page, size },
      headers: TaskService.getAuthHeaders(),
    });
    return response.data as PaginatedResponse<Task>;
  }

  async getTask(accountId: string, taskId: string): Promise<Task> {
    const response = await this.apiClient.get(
      `/accounts/${accountId}/tasks/${taskId}`,
      {
        headers: TaskService.getAuthHeaders(),
      },
    );
    return response.data as Task;
  }

  async updateTask(
    accountId: string,
    taskId: string,
    data: UpdateTaskRequest,
  ): Promise<Task> {
    const response = await this.apiClient.patch(
      `/accounts/${accountId}/tasks/${taskId}`,
      data,
      {
        headers: TaskService.getAuthHeaders(),
      },
    );
    return response.data as Task;
  }

  async deleteTask(accountId: string, taskId: string): Promise<void> {
    await this.apiClient.delete(`/accounts/${accountId}/tasks/${taskId}`, {
      headers: TaskService.getAuthHeaders(),
    });
  }

  // Comment APIs
  async createComment(
    accountId: string,
    taskId: string,
    data: CreateCommentRequest,
  ): Promise<Comment> {
    const response = await this.apiClient.post(
      `/accounts/${accountId}/tasks/${taskId}/comments`,
      data,
      {
        headers: TaskService.getAuthHeaders(),
      },
    );
    return response.data as Comment;
  }

  async getComments(
    accountId: string,
    taskId: string,
    page: number = 1,
    size: number = 10,
  ): Promise<PaginatedResponse<Comment>> {
    const response = await this.apiClient.get(
      `/accounts/${accountId}/tasks/${taskId}/comments`,
      {
        params: { page, size },
        headers: TaskService.getAuthHeaders(),
      },
    );
    return response.data as PaginatedResponse<Comment>;
  }

  async getComment(
    accountId: string,
    taskId: string,
    commentId: string,
  ): Promise<Comment> {
    const response = await this.apiClient.get(
      `/accounts/${accountId}/tasks/${taskId}/comments/${commentId}`,
      {
        headers: TaskService.getAuthHeaders(),
      },
    );
    return response.data as Comment;
  }

  async updateComment(
    accountId: string,
    taskId: string,
    commentId: string,
    data: UpdateCommentRequest,
  ): Promise<Comment> {
    const response = await this.apiClient.patch(
      `/accounts/${accountId}/tasks/${taskId}/comments/${commentId}`,
      data,
      {
        headers: TaskService.getAuthHeaders(),
      },
    );
    return response.data as Comment;
  }

  async deleteComment(
    accountId: string,
    taskId: string,
    commentId: string,
  ): Promise<void> {
    await this.apiClient.delete(
      `/accounts/${accountId}/tasks/${taskId}/comments/${commentId}`,
      {
        headers: TaskService.getAuthHeaders(),
      },
    );
  }
}

export const taskService = new TaskService();
