import { JsonObject } from './common-types';

export class Task {
  id: string;
  accountId: string;
  title: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
  active: boolean;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.accountId = json.account_id as string;
    this.title = json.title as string;
    this.description = json.description as string;
    this.createdAt = json.created_at ? new Date(json.created_at as string) : new Date();
    this.updatedAt = json.updated_at ? new Date(json.updated_at as string) : new Date();
    this.active = json.active as boolean ?? true;
  }
}