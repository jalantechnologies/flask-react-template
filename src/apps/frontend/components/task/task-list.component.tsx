import React, { useState, useEffect, useMemo } from 'react';
import clsx from 'clsx';

import { Button, FormControl, Input, ParagraphMedium } from 'frontend/components';
import { H2 } from 'frontend/components/typography';
import {
  Task,
  PaginationParams,
} from 'frontend/types';
import { ButtonType, ButtonKind } from 'frontend/types/button';
import TaskItem from './task-item.component';
import TaskService, { TaskFilters, TaskListResponse } from 'frontend/services/task.service';

interface TaskListProps {
  accountId: string;
  currentAccountId: string;
  onTaskUpdate?: (taskId: string, task: Task) => void;
  onTaskDelete?: (taskId: string) => void;
  className?: string;
  showSearch?: boolean;
  showFilters?: boolean;
  pageSize?: number;
}

const TaskList: React.FC<TaskListProps> = ({
  accountId,
  currentAccountId,
  onTaskUpdate,
  onTaskDelete,
  className,
  showSearch = true,
  showFilters = true,
  pageSize = 10,
}) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [pagination, setPagination] = useState({
    totalCount: 0,
    totalPages: 0,
    currentPage: 1,
    pageSize,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<TaskFilters>({
    status: 'all',
    sortBy: 'created_at',
    sortOrder: 'desc',
  });

  const taskService = new TaskService();

  // Load tasks
  const loadTasks = async (page: number = 1, append: boolean = false) => {
    try {
      setIsLoading(true);
      setError(null);

      const paginationParams = new PaginationParams(page, pageSize);
      const response = await taskService.getTasks(accountId, paginationParams, {
        ...filters,
        search: searchQuery || undefined,
      });

      if (response.data) {
        if (append) {
          setTasks(prev => [...prev, ...response.data!.items]);
        } else {
          setTasks(response.data.items);
        }

        setPagination({
          totalCount: response.data.totalCount,
          totalPages: response.data.totalPages,
          currentPage: page,
          pageSize,
        });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load tasks';
      setError(errorMessage);
      console.error('Error loading tasks:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load and reload on filters/search change
  useEffect(() => {
    loadTasks(1, false);
  }, [accountId, searchQuery, filters]);

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  // Handle filter change
  const handleFilterChange = (newFilters: Partial<TaskFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  // Handle pagination
  const handleLoadMore = () => {
    if (pagination.currentPage < pagination.totalPages) {
      loadTasks(pagination.currentPage + 1, true);
    }
  };

  // Handle task update
  const handleTaskUpdate = (updatedTask: Task) => {
    setTasks(prev => prev.map(task =>
      task.id === updatedTask.id ? updatedTask : task
    ));
    onTaskUpdate?.(updatedTask.id, updatedTask);
  };

  // Handle task delete
  const handleTaskDelete = (taskId: string) => {
    setTasks(prev => prev.filter(task => task.id !== taskId));
    setPagination(prev => ({
      ...prev,
      totalCount: prev.totalCount - 1,
    }));
    onTaskDelete?.(taskId);
  };

  // Memoized filtered tasks (for client-side filtering as backup)
  const filteredTasks = useMemo(() => {
    if (!searchQuery && filters.status === 'all') {
      return tasks;
    }

    return tasks.filter(task => {
      // Search filter
      if (searchQuery && !task.matchesSearchQuery(searchQuery)) {
        return false;
      }

      // Status filter (if implemented)
      // if (filters.status !== 'all') {
      //   return task.status === filters.status;
      // }

      return true;
    });
  }, [tasks, searchQuery, filters]);

  const hasMore = pagination.currentPage < pagination.totalPages;
  const noResults = !isLoading && tasks.length === 0 && !error;

  return (
    <div className={clsx('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <H2>Tasks ({pagination.totalCount})</H2>
        {pagination.totalCount > tasks.length && (
          <span className="text-sm text-gray-500">
            Showing {tasks.length} of {pagination.totalCount}
          </span>
        )}
      </div>

      {/* Search and Filters */}
      {(showSearch || showFilters) && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-4">
          {/* Search */}
          {showSearch && (
            <div className="flex-1">
              <FormControl label="Search Tasks" error={null}>
                <Input
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  placeholder="Search by title or description..."
                  disabled={isLoading}
                  className="max-w-md"
                />
              </FormControl>
            </div>
          )}

          {/* Filters */}
          {showFilters && (
            <div className="flex flex-wrap gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sort By
                </label>
                <select
                  value={filters.sortBy}
                  onChange={(e) => handleFilterChange({ sortBy: e.target.value as any })}
                  disabled={isLoading}
                  className="rounded-md border border-gray-300 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="created_at">Created Date</option>
                  <option value="updated_at">Updated Date</option>
                  <option value="title">Title</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Order
                </label>
                <select
                  value={filters.sortOrder}
                  onChange={(e) => handleFilterChange({ sortOrder: e.target.value as any })}
                  disabled={isLoading}
                  className="rounded-md border border-gray-300 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="desc">Newest First</option>
                  <option value="asc">Oldest First</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange({ status: e.target.value as any })}
                  disabled={isLoading}
                  className="rounded-md border border-gray-300 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="all">All Tasks</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {isLoading && tasks.length === 0 && (
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-500">Loading tasks...</div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-red-700 mb-3">{error}</div>
          <Button
            type={ButtonType.BUTTON}
            kind={ButtonKind.TERTIARY}
            onClick={() => loadTasks(1, false)}
          >
            Retry
          </Button>
        </div>
      )}

      {/* No Results */}
      {noResults && (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <div className="text-gray-500 mb-4">
            {searchQuery ? 'No tasks found matching your search.' : 'No tasks found.'}
          </div>
          {searchQuery && (
            <Button
              type={ButtonType.BUTTON}
              kind={ButtonKind.TERTIARY}
              onClick={() => setSearchQuery('')}
            >
              Clear Search
            </Button>
          )}
        </div>
      )}

      {/* Tasks List */}
      {!isLoading && !error && tasks.length > 0 && (
        <div className="space-y-4">
          {filteredTasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              currentAccountId={currentAccountId}
              onUpdate={handleTaskUpdate}
              onDelete={handleTaskDelete}
            />
          ))}

          {/* Load More Button */}
          {hasMore && (
            <div className="flex justify-center pt-6">
              <Button
                type={ButtonType.BUTTON}
                kind={ButtonKind.SECONDARY}
                onClick={handleLoadMore}
                isLoading={isLoading}
                disabled={isLoading}
                className="w-full max-w-xs"
              >
                {isLoading ? 'Loading...' : 'Load More Tasks'}
              </Button>
            </div>
          )}

          {/* End of Results */}
          {!hasMore && filteredTasks.length > 0 && (
            <div className="text-center py-4 text-sm text-gray-500">
              Showing all {pagination.totalCount} tasks
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TaskList;