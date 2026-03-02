import { JsonObject } from 'frontend/types/common-types';

export class PaginationParams {
  page: number;
  size: number;
  total_count: number;
  total_pages: number;

  constructor(json: JsonObject) {
    this.page = json.page as number;
    this.size = json.size as number;
    this.total_count = json.total_count as number;
    this.total_pages = json.total_pages as number;
  }
}

export class PaginationResult<T> {
  items: T[];
  paginationParams: PaginationParams;
  totalCount: number;

  constructor(items: T[], paginationParams: PaginationParams, totalCount: number) {
    this.items = items;
    this.paginationParams = paginationParams;
    this.totalCount = totalCount;
  }
}

export class Task {
  id: string;
  accountId: string;
  title: string;
  description: string;
  active: boolean;
  createdAt: string;
  updatedAt: string;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.accountId = json.account_id as string;
    this.title = json.title as string;
    this.description = json.description as string;
    this.active = json.active as boolean;
    this.createdAt = json.created_at as string;
    this.updatedAt = json.updated_at as string;
  }
}

export class Comment {
  id: string;
  accountId: string;
  taskId: string;
  content: string;
  active: boolean;
  createdAt: string;
  updatedAt: string;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.accountId = json.account_id as string;
    this.taskId = json.task_id as string;
    this.content = json.content as string;
    this.active = json.active as boolean;
    this.createdAt = json.created_at as string;
    this.updatedAt = json.updated_at as string;
  }
}
