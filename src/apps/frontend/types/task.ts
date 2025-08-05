export interface Task {
  id: string;
  account_id: string;
  title: string;
  description: string;
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

export interface PaginatedTasksResponse {
  items: Task[];
  total_count: number;
  page: number;
  size: number;
}
