import { JsonObject } from 'frontend/types/common-types';

export class Comment {
  id: string;
  accountId: string;
  taskId: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
  active: boolean;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.accountId = json.account_id as string;
    this.taskId = json.task_id as string;
    this.content = json.content as string;
    this.createdAt = new Date(json.created_at as string);
    this.updatedAt = new Date(json.updated_at as string);
    this.active = json.active as boolean;
  }
}