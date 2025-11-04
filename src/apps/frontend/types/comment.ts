import { JsonObject } from 'frontend/types/common-types';

export class Comment {
  id: string;
  taskId: string;
  accountId: string;
  authorName: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.taskId = json.task_id as string;
    this.accountId = json.account_id as string;
    this.authorName = json.author_name as string;
    this.content = json.content as string;
    this.createdAt = new Date(json.created_at as string);
    this.updatedAt = new Date(json.updated_at as string);
  }

  toJson(): JsonObject {
    return {
      id: this.id,
      task_id: this.taskId,
      account_id: this.accountId,
      author_name: this.authorName,
      content: this.content,
      created_at: this.createdAt,
      updated_at: this.updatedAt,
    };
  }

  isOwnedBy(accountId: string): boolean {
    return this.accountId === accountId;
  }

  wasUpdated(): boolean {
    return this.createdAt.getTime() !== this.updatedAt.getTime();
  }
}

export class CreateCommentRequest {
  content: string;

  constructor(content: string) {
    this.content = content;
  }

  toJson(): JsonObject {
    return {
      content: this.content,
    };
  }
}

export class UpdateCommentRequest {
  content: string;

  constructor(content: string) {
    this.content = content;
  }

  toJson(): JsonObject {
    return {
      content: this.content,
    };
  }
}

export class PaginationParams {
  page: number;
  size: number;
  offset: number;

  constructor(page: number = 1, size: number = 10) {
    this.page = page;
    this.size = size;
    this.offset = (page - 1) * size;
  }

  toJson(): JsonObject {
    return {
      page: this.page,
      size: this.size,
      offset: this.offset,
    };
  }
}

export class CommentListResponse {
  items: Comment[];
  totalCount: number;
  totalPages: number;
  paginationParams: {
    page: number;
    size: number;
    offset: number;
  };

  constructor(json: JsonObject) {
    this.items = (json.items as JsonObject[]).map(item => new Comment(item));
    this.totalCount = json.total_count as number;
    this.totalPages = json.total_pages as number;
    this.paginationParams = json.pagination_params as {
      page: number;
      size: number;
      offset: number;
    };
  }
}

export class CommentDeletionResult {
  commentId: string;
  deletedAt: Date;
  success: boolean;

  constructor(json: JsonObject) {
    this.commentId = json.comment_id as string;
    this.deletedAt = new Date(json.deleted_at as string);
    this.success = json.success as boolean;
  }
}