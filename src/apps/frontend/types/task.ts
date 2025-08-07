export interface Task {
  id: string;
  title: string;
  description: string;
  account_id: string;
}

export interface CreateTaskRequest {
  title: string;
  description: string;
}

export interface UpdateTaskRequest {
  title: string;
  description: string;
}

export interface TasksResponse {
  items: Task[];
  total_count: number;
  pagination_params: {
    page: number;
    size: number;
    offset: number;
  };
  total_pages: number;
}
