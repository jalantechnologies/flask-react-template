export interface Task {
  id: string;
  account_id: string;
  title: string;
  description: string;
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
  pagination_params: {
    page: number;
    size: number;
    offset: number;
  };
  total_count: number;
  total_pages: number;
}

export interface TaskFormData {
  title: string;
  description: string;
}

export interface Comment {
  id: string;
  task_id: string;
  account_id: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CreateCommentRequest {
  content: string;
}

export interface UpdateCommentRequest {
  content: string;
}

export interface CommentsResponse {
  items: Comment[];
  pagination_params: {
    page: number;
    size: number;
    offset: number;
  };
  total_count: number;
  total_pages: number;
}

export interface CommentFormData {
  content: string;
}
