import { JsonObject } from 'frontend/types/common-types';

export interface TaskApiResponse {
  id: string;
  account_id: string;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export class Task {
  id: string;
  accountId: string;
  title: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.accountId = json.account_id as string;
    this.title = json.title as string;
    this.description = json.description as string;
    this.createdAt = new Date(json.created_at as string);
    this.updatedAt = new Date(json.updated_at as string);
  }

  displayCreatedAt(): string {
    return this.createdAt.toLocaleDateString();
  }

  displayUpdatedAt(): string {
    return this.updatedAt.toLocaleDateString();
  }
}

export interface CreateTaskRequest {
  title: string;
  description: string;
}

export interface UpdateTaskRequest {
  title: string;
  description: string;
}

export interface TasksListResponse {
  items: TaskApiResponse[];
  total: number;
  page: number;
  size: number;
  has_more: boolean;
}

export interface PaginationParams {
  page?: number;
  size?: number;
}