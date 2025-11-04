import TaskService, { TaskFilters } from '../task.service';
import { ApiResponse } from 'frontend/types';

// Mock the APIService
jest.mock('../api.service', () => {
  return {
    default: class MockAPIService {
      apiClient = {
        get: jest.fn(),
        post: jest.fn(),
        patch: jest.fn(),
        delete: jest.fn(),
      };
    },
  };
});

describe('TaskService', () => {
  let taskService: TaskService;
  let mockApiClient: any;

  beforeEach(() => {
    taskService = new TaskService();
    mockApiClient = taskService['apiClient'];
    jest.clearAllMocks();
  });

  describe('getTasks', () => {
    it('should fetch tasks with default parameters', async () => {
      const mockResponse = {
        data: {
          items: [{ id: '1', title: 'Test Task' }],
          total_count: 1,
          total_pages: 1,
          pagination_params: { page: 1, size: 10, offset: 0 },
        },
      };

      mockApiClient.get.mockResolvedValue(mockResponse);

      const result = await taskService.getTasks('account-123');

      expect(mockApiClient.get).toHaveBeenCalledWith(
        '/accounts/account-123/tasks?page=1&size=10'
      );
      expect(result.data).toEqual({
        items: [{ id: '1', title: 'Test Task' }],
        totalCount: 1,
        totalPages: 1,
        paginationParams: { page: 1, size: 10, offset: 0 },
      });
    });

    it('should include filters in query parameters', async () => {
      const filters: TaskFilters = {
        status: 'active',
        search: 'test query',
        sortBy: 'title',
        sortOrder: 'asc',
      };

      mockApiClient.get.mockResolvedValue({ data: { items: [] } });

      await taskService.getTasks('account-123', undefined, filters);

      expect(mockApiClient.get).toHaveBeenCalledWith(
        '/accounts/account-123/tasks?page=1&size=10&status=active&search=test+query&sort_by=title&sort_order=asc'
      );
    });

    it('should handle empty response gracefully', async () => {
      mockApiClient.get.mockResolvedValue({ data: {} });

      const result = await taskService.getTasks('account-123');

      expect(result.data).toEqual({
        items: [],
        totalCount: 0,
        totalPages: 0,
        paginationParams: { page: 1, size: 10, offset: 0 },
      });
    });
  });

  describe('getTask', () => {
    it('should fetch a single task', async () => {
      const mockTask = {
        id: '1',
        title: 'Test Task',
        description: 'Test Description',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      mockApiClient.get.mockResolvedValue({ data: mockTask });

      const result = await taskService.getTask('account-123', 'task-1');

      expect(mockApiClient.get).toHaveBeenCalledWith('/accounts/account-123/tasks/task-1');
      expect(result.data?.id).toBe('1');
      expect(result.data?.title).toBe('Test Task');
    });

    it('should handle fetch errors', async () => {
      mockApiClient.get.mockRejectedValue(new Error('Network error'));

      await expect(taskService.getTask('account-123', 'task-1')).rejects.toThrow(
        'Failed to fetch task: Error: Network error'
      );
    });
  });

  describe('createTask', () => {
    it('should create a task with valid data', async () => {
      const mockTask = {
        id: '1',
        title: 'New Task',
        description: 'New Description',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      mockApiClient.post.mockResolvedValue({ data: mockTask });

      const result = await taskService.createTask('account-123', 'New Task', 'New Description');

      expect(mockApiClient.post).toHaveBeenCalledWith('/accounts/account-123/tasks', {
        title: 'New Task',
        description: 'New Description',
      });
      expect(result.data?.title).toBe('New Task');
    });

    it('should trim whitespace from inputs', async () => {
      const mockTask = { id: '1', title: 'Trimmed Task' };
      mockApiClient.post.mockResolvedValue({ data: mockTask });

      await taskService.createTask('account-123', '  Trimmed Task  ', '  Trimmed Description  ');

      expect(mockApiClient.post).toHaveBeenCalledWith('/accounts/account-123/tasks', {
        title: 'Trimmed Task',
        description: 'Trimmed Description',
      });
    });

    it('should validate title is required', async () => {
      await expect(taskService.createTask('account-123', '', 'Description')).rejects.toThrow(
        'Task title is required'
      );
      expect(mockApiClient.post).not.toHaveBeenCalled();
    });

    it('should validate title length', async () => {
      const longTitle = 'x'.repeat(201);

      await expect(taskService.createTask('account-123', longTitle, 'Description')).rejects.toThrow(
        'Task title cannot exceed 200 characters'
      );
      expect(mockApiClient.post).not.toHaveBeenCalled();
    });

    it('should validate description length', async () => {
      const longDescription = 'x'.repeat(2001);

      await expect(taskService.createTask('account-123', 'Title', longDescription)).rejects.toThrow(
        'Task description cannot exceed 2000 characters'
      );
      expect(mockApiClient.post).not.toHaveBeenCalled();
    });

    it('should handle creation errors', async () => {
      mockApiClient.post.mockRejectedValue(new Error('Creation failed'));

      await expect(taskService.createTask('account-123', 'Title', 'Description')).rejects.toThrow(
        'Failed to create task: Error: Creation failed'
      );
    });
  });

  describe('updateTask', () => {
    it('should update a task with valid data', async () => {
      const mockTask = {
        id: '1',
        title: 'Updated Task',
        description: 'Updated Description',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      mockApiClient.patch.mockResolvedValue({ data: mockTask });

      const result = await taskService.updateTask('account-123', 'task-1', 'Updated Task', 'Updated Description');

      expect(mockApiClient.patch).toHaveBeenCalledWith('/accounts/account-123/tasks/task-1', {
        title: 'Updated Task',
        description: 'Updated Description',
      });
      expect(result.data?.title).toBe('Updated Task');
    });

    it('should validate update data', async () => {
      await expect(taskService.updateTask('account-123', 'task-1', '', 'Description')).rejects.toThrow(
        'Task title is required'
      );
      expect(mockApiClient.patch).not.toHaveBeenCalled();
    });

    it('should handle update errors', async () => {
      mockApiClient.patch.mockRejectedValue(new Error('Update failed'));

      await expect(taskService.updateTask('account-123', 'task-1', 'Title', 'Description')).rejects.toThrow(
        'Failed to update task: Error: Update failed'
      );
    });
  });

  describe('deleteTask', () => {
    it('should delete a task', async () => {
      mockApiClient.delete.mockResolvedValue({});

      const result = await taskService.deleteTask('account-123', 'task-1');

      expect(mockApiClient.delete).toHaveBeenCalledWith('/accounts/account-123/tasks/task-1');
      expect(result.data).toBeUndefined();
    });

    it('should handle deletion errors', async () => {
      mockApiClient.delete.mockRejectedValue(new Error('Delete failed'));

      await expect(taskService.deleteTask('account-123', 'task-1')).rejects.toThrow(
        'Failed to delete task: Error: Delete failed'
      );
    });
  });

  describe('searchTasks', () => {
    it('should search tasks with query', async () => {
      mockApiClient.get.mockResolvedValue({ data: { items: [] } });

      await taskService.searchTasks('account-123', 'search query');

      expect(mockApiClient.get).toHaveBeenCalledWith(
        '/accounts/account-123/tasks?page=1&size=10&search=search+query&status=all&sort_by=created_at&sort_order=desc'
      );
    });
  });

  describe('getTaskStats', () => {
    it('should fetch task statistics', async () => {
      const mockTaskListResponse = {
        data: {
          items: [],
          total_count: 5,
          total_pages: 1,
          pagination_params: { page: 1, size: 5, offset: 0 },
        },
      };

      mockApiClient.get.mockResolvedValue(mockTaskListResponse);

      const result = await taskService.getTaskStats('account-123');

      expect(mockApiClient.get).toHaveBeenCalledWith(
        '/accounts/account-123/tasks?page=1&size=5&sort_by=created_at&sort_order=desc&status=all'
      );
      expect(result.data).toEqual({
        total: 5,
        active: 0,
        completed: 0,
        recent: [],
      });
    });

    it('should handle stats errors', async () => {
      mockApiClient.get.mockRejectedValue(new Error('Stats fetch failed'));

      await expect(taskService.getTaskStats('account-123')).rejects.toThrow(
        'Failed to fetch task statistics: Error: Stats fetch failed'
      );
    });
  });

  describe('bulkDeleteTasks', () => {
    it('should delete multiple tasks', async () => {
      mockApiClient.delete.mockResolvedValue({});

      const result = await taskService.bulkDeleteTasks('account-123', ['task-1', 'task-2']);

      expect(mockApiClient.delete).toHaveBeenCalledTimes(2);
      expect(mockApiClient.delete).toHaveBeenCalledWith('/accounts/account-123/tasks/task-1');
      expect(mockApiClient.delete).toHaveBeenCalledWith('/accounts/account-123/tasks/task-2');
      expect(result.data).toEqual({
        deletedCount: 2,
        errors: [],
      });
    });

    it('should handle partial failures in bulk delete', async () => {
      mockApiClient.delete
        .mockResolvedValueOnce({})
        .mockRejectedValueOnce(new Error('Delete failed'));

      const result = await taskService.bulkDeleteTasks('account-123', ['task-1', 'task-2']);

      expect(result.data).toEqual({
        deletedCount: 1,
        errors: ['Failed to delete task task-2: Error: Delete failed'],
      });
    });
  });
});