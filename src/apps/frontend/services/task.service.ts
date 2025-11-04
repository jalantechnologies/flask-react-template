import APIService from 'frontend/services/api.service';
import {
  ApiResponse,
  Task,
  PaginationParams,
} from 'frontend/types';

export interface TaskListResponse {
  items: Task[];
  totalCount: number;
  totalPages: number;
  paginationParams: {
    page: number;
    size: number;
    offset: number;
  };
}

export interface TaskFilters {
  status?: 'all' | 'active' | 'completed';
  search?: string;
  sortBy?: 'created_at' | 'updated_at' | 'title';
  sortOrder?: 'asc' | 'desc';
}

export default class TaskService extends APIService {
  /**
   * Get all tasks for an account with pagination and filtering
   */
  getTasks = async (
    accountId: string,
    paginationParams?: PaginationParams,
    filters?: TaskFilters,
  ): Promise<ApiResponse<TaskListResponse>> => {
    const params = paginationParams || new PaginationParams();
    const queryParams = new URLSearchParams({
      page: params.page.toString(),
      size: params.size.toString(),
    });

    // Add filters to query params
    if (filters) {
      if (filters.status && filters.status !== 'all') {
        queryParams.append('status', filters.status);
      }
      if (filters.search) {
        queryParams.append('search', filters.search.trim());
      }
      if (filters.sortBy) {
        queryParams.append('sort_by', filters.sortBy);
      }
      if (filters.sortOrder) {
        queryParams.append('sort_order', filters.sortOrder);
      }
    }

    const response = await this.apiClient.get(
      `/accounts/${accountId}/tasks?${queryParams.toString()}`,
    );

    // Transform response to match TaskListResponse interface
    const responseData = {
      items: response.data.items || [],
      totalCount: response.data.total_count || 0,
      totalPages: response.data.total_pages || 0,
      paginationParams: response.data.pagination_params || {
        page: params.page,
        size: params.size,
        offset: params.offset,
      },
    };

    return new ApiResponse(responseData);
  };

  /**
   * Get a single task by ID
   */
  getTask = async (
    accountId: string,
    taskId: string,
  ): Promise<ApiResponse<Task>> => {
    try {
      const response = await this.apiClient.get(
        `/accounts/${accountId}/tasks/${taskId}`,
      );
      return new ApiResponse(new Task(response.data));
    } catch (error) {
      throw new Error(`Failed to fetch task: ${error}`);
    }
  };

  /**
   * Create a new task with validation
   */
  createTask = async (
    accountId: string,
    title: string,
    description: string,
  ): Promise<ApiResponse<Task>> => {
    // Validate inputs
    const trimmedTitle = title.trim();
    const trimmedDescription = description.trim();

    if (!trimmedTitle) {
      throw new Error('Task title is required');
    }

    if (trimmedTitle.length > 200) {
      throw new Error('Task title cannot exceed 200 characters');
    }

    if (trimmedDescription.length > 2000) {
      throw new Error('Task description cannot exceed 2000 characters');
    }

    try {
      const response = await this.apiClient.post(
        `/accounts/${accountId}/tasks`,
        {
          title: trimmedTitle,
          description: trimmedDescription,
        },
      );
      return new ApiResponse(new Task(response.data));
    } catch (error) {
      throw new Error(`Failed to create task: ${error}`);
    }
  };

  /**
   * Update an existing task with validation
   */
  updateTask = async (
    accountId: string,
    taskId: string,
    title: string,
    description: string,
  ): Promise<ApiResponse<Task>> => {
    // Validate inputs
    const trimmedTitle = title.trim();
    const trimmedDescription = description.trim();

    if (!trimmedTitle) {
      throw new Error('Task title is required');
    }

    if (trimmedTitle.length > 200) {
      throw new Error('Task title cannot exceed 200 characters');
    }

    if (trimmedDescription.length > 2000) {
      throw new Error('Task description cannot exceed 2000 characters');
    }

    try {
      const response = await this.apiClient.patch(
        `/accounts/${accountId}/tasks/${taskId}`,
        {
          title: trimmedTitle,
          description: trimmedDescription,
        },
      );
      return new ApiResponse(new Task(response.data));
    } catch (error) {
      throw new Error(`Failed to update task: ${error}`);
    }
  };

  /**
   * Delete a task with confirmation
   */
  deleteTask = async (
    accountId: string,
    taskId: string,
  ): Promise<ApiResponse<void>> => {
    try {
      await this.apiClient.delete(
        `/accounts/${accountId}/tasks/${taskId}`,
      );
      return new ApiResponse();
    } catch (error) {
      throw new Error(`Failed to delete task: ${error}`);
    }
  };

  /**
   * Bulk operations for multiple tasks
   */
  bulkDeleteTasks = async (
    accountId: string,
    taskIds: string[],
  ): Promise<ApiResponse<{ deletedCount: number; errors: string[] }>> => {
    const results = {
      deletedCount: 0,
      errors: [] as string[],
    };

    for (const taskId of taskIds) {
      try {
        await this.deleteTask(accountId, taskId);
        results.deletedCount++;
      } catch (error) {
        results.errors.push(`Failed to delete task ${taskId}: ${error}`);
      }
    }

    return new ApiResponse(results);
  };

  /**
   * Search tasks with advanced filtering
   */
  searchTasks = async (
    accountId: string,
    query: string,
    paginationParams?: PaginationParams,
  ): Promise<ApiResponse<TaskListResponse>> => {
    return this.getTasks(paginationParams, {
      search: query,
      status: 'all',
      sortBy: 'created_at',
      sortOrder: 'desc',
    });
  };

  /**
   * Get task statistics
   */
  getTaskStats = async (
    accountId: string,
  ): Promise<ApiResponse<{
    total: number;
    active: number;
    completed: number;
    recent: Task[];
  }>> => {
    try {
      // Get recent tasks
      const recentResponse = await this.getTasks(accountId, new PaginationParams(1, 5), {
        sortBy: 'created_at',
        sortOrder: 'desc',
        status: 'all',
      });

      const stats = {
        total: recentResponse.data?.totalCount || 0,
        active: 0, // This would be calculated based on actual task status
        completed: 0, // This would be calculated based on actual task status
        recent: recentResponse.data?.items || [],
      };

      return new ApiResponse(stats);
    } catch (error) {
      throw new Error(`Failed to fetch task statistics: ${error}`);
    }
  };
}