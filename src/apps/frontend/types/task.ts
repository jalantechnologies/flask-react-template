import { JsonObject } from 'frontend/types/common-types';

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

  isOwnedBy(accountId: string): boolean {
    return this.accountId === accountId;
  }

  wasUpdated(): boolean {
    return this.createdAt.getTime() !== this.updatedAt.getTime();
  }

  getFormattedDate(): string {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(this.createdAt);
  }

  getFormattedUpdatedDate(): string {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(this.updatedAt);
  }

  getTruncatedDescription(maxLength: number = 100): string {
    if (this.description.length <= maxLength) {
      return this.description;
    }
    return this.description.substring(0, maxLength).trim() + '...';
  }

  getTruncatedTitle(maxLength: number = 50): string {
    if (this.title.length <= maxLength) {
      return this.title;
    }
    return this.title.substring(0, maxLength).trim() + '...';
  }

  matchesSearchQuery(query: string): boolean {
    if (!query.trim()) return true;

    const searchTerms = query.toLowerCase().trim().split(/\s+/);
    const searchableText = `${this.title} ${this.description}`.toLowerCase();

    return searchTerms.every(term => searchableText.includes(term));
  }

  getWordCount(): number {
    return this.description.split(/\s+/).filter(word => word.length > 0).length;
  }

  getReadingTime(): string {
    const wordsPerMinute = 200;
    const wordCount = this.getWordCount();
    const minutes = Math.ceil(wordCount / wordsPerMinute);
    return `${minutes} min read`;
  }
}

export class CreateTaskRequest {
  title: string;
  description: string;

  constructor(title: string, description: string) {
    this.title = title.trim();
    this.description = description.trim();
  }

  toJson(): JsonObject {
    return {
      title: this.title,
      description: this.description,
    };
  }

  validate(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.title) {
      errors.push('Task title is required');
    }

    if (this.title.length > 200) {
      errors.push('Task title cannot exceed 200 characters');
    }

    if (this.description.length > 2000) {
      errors.push('Task description cannot exceed 2000 characters');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }
}

export class UpdateTaskRequest {
  title: string;
  description: string;

  constructor(title: string, description: string) {
    this.title = title.trim();
    this.description = description.trim();
  }

  toJson(): JsonObject {
    return {
      title: this.title,
      description: this.description,
    };
  }

  validate(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.title) {
      errors.push('Task title is required');
    }

    if (this.title.length > 200) {
      errors.push('Task title cannot exceed 200 characters');
    }

    if (this.description.length > 2000) {
      errors.push('Task description cannot exceed 2000 characters');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }
}

export interface TaskFormData {
  title: string;
  description: string;
}

export interface TaskValidationError {
  title?: string;
  description?: string;
  general?: string;
}