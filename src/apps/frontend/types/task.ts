export interface Task {
  id: string;
  account_id: string;
  title: string;
  description: string;
  active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreateTaskRequest {
  title: string;
  description: string;
}

export interface UpdateTaskRequest {
  title: string;
  description: string;
}

export interface PaginatedTasksResponse {
  items: Task[];
  pagination: {
    page: number;
    size: number;
    total: number;
    total_pages: number;
  };
}
