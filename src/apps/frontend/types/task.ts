import { JsonObject, Nullable } from 'frontend/types/common-types';

export interface CreateTaskRequest {
  title: string;
  description: string;
}

export interface UpdateTaskRequest {
  title: string;
  description: string;
}

export interface Task {
  id: string;
  account_id: string;
  title: string;
  description: string;
  created_at?: string;
  updated_at?: string;
}

export interface PaginatedTasksResponse {
  items: Task[];
  total_count: number;
  pagination_params: {
    page: number;
    size: number;
  };
}

export interface TaskFilters {
  page?: number;
  size?: number;
}

export class TaskModel {
  id: string;
  accountId: string;
  title: string;
  description: string;
  createdAt?: string;
  updatedAt?: string;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.accountId = json.account_id as string;
    this.title = json.title as string;
    this.description = json.description as string;
    this.createdAt = json.created_at as string;
    this.updatedAt = json.updated_at as string;
  }

  static fromJson(json: JsonObject): TaskModel {
    return new TaskModel(json);
  }

  toJson(): JsonObject {
    return {
      id: this.id,
      account_id: this.accountId,
      title: this.title,
      description: this.description,
      created_at: this.createdAt,
      updated_at: this.updatedAt,
    };
  }
} 