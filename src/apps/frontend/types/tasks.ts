import { JsonObject } from 'frontend/types/common-types';

export class Task {
  id: string;
  title: string;
  description: string;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.title = json.title as string;
    this.description = json.description as string;
  }

  displayName(): string {
    return `${this.title} ${this.description}`.trim();
  }
}
