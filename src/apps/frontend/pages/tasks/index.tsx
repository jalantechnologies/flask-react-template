import React, { useCallback, useEffect, useMemo, useState } from 'react';

import Button from 'frontend/components/button';
import HorizontalStackLayout from 'frontend/components/layouts/horizontal-stack-layout';
import VerticalStackLayout from 'frontend/components/layouts/vertical-stack-layout';
import { TaskForm, TaskList } from 'frontend/components/task';
import { TaskService } from 'frontend/services';
import { ButtonKind, Task, TaskFormData, TasksResponse } from 'frontend/types';
import { useAsyncOperation } from 'frontend/contexts/async.hook';
import { Logger } from 'frontend/utils/logger';

const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  const taskService = useMemo(() => new TaskService(), []);

  const getTasksFn = useCallback(
    async (page: number, size: number) => taskService.getTasks(page, size),
    [taskService],
  );
  const createTaskFn = useCallback(
    async (data: TaskFormData) => taskService.createTask(data),
    [taskService],
  );
  const updateTaskFn = useCallback(
    async (taskId: string, data: TaskFormData) =>
      taskService.updateTask(taskId, data),
    [taskService],
  );
  const deleteTaskFn = useCallback(
    async (taskId: string) => taskService.deleteTask(taskId),
    [taskService],
  );

  const { asyncCallback: executeLoadTasks, isLoading: isLoadingTasks } =
    useAsyncOperation<TasksResponse>(getTasksFn);

  const { asyncCallback: executeCreateTask, isLoading: isCreatingTask } =
    useAsyncOperation<Task>(createTaskFn);

  const { asyncCallback: executeUpdateTask, isLoading: isUpdatingTask } =
    useAsyncOperation<Task>(updateTaskFn);

  const { asyncCallback: executeDeleteTask, isLoading: isDeletingTask } =
    useAsyncOperation<void>(deleteTaskFn);

  const loadTasks = useCallback(
    async (page: number = 1, append: boolean = false) => {
      try {
        const response = await executeLoadTasks(page, 10);
        if (response) {
          const tasksData = response;
          setTasks((prev) =>
            append ? [...prev, ...tasksData.items] : tasksData.items,
          );
          setCurrentPage(page);
          setHasMore(page < tasksData.total_pages);
        }
      } catch (error) {
        Logger.error('Failed to load tasks', error);
      }
    },
    [executeLoadTasks],
  );

  const handleCreateTask = async (data: TaskFormData) => {
    try {
      const response = await executeCreateTask(data);
      if (response) {
        setTasks((prev) => [response, ...prev]);
        setShowCreateForm(false);
        Logger.info('Task created successfully');
      }
    } catch (error) {
      Logger.error('Failed to create task', error);
    }
  };

  const handleEditTask = async (taskId: string, data: TaskFormData) => {
    try {
      const response = await executeUpdateTask(taskId, data);
      if (response) {
        setTasks((prev) =>
          prev.map((task) => (task.id === taskId ? response : task)),
        );
        Logger.info('Task updated successfully');
      }
    } catch (error) {
      Logger.error('Failed to update task', error);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await executeDeleteTask(taskId);
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
      Logger.info('Task deleted successfully');
    } catch (error) {
      Logger.error('Failed to delete task', error);
    }
  };

  const handleLoadMore = () => {
    if (hasMore && !isLoadingTasks) {
      loadTasks(currentPage + 1, true);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const isLoading =
    isLoadingTasks || isCreatingTask || isUpdatingTask || isDeletingTask;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <VerticalStackLayout gap={6}>
        {/* Header */}
        <HorizontalStackLayout>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
            <p className="text-gray-600 mt-1">
              Manage your tasks and stay organized
            </p>
          </div>
          <Button
            kind={ButtonKind.PRIMARY}
            onClick={() => setShowCreateForm(!showCreateForm)}
            disabled={isLoading}
          >
            {showCreateForm ? 'Cancel' : 'New Task'}
          </Button>
        </HorizontalStackLayout>

        {/* Create Task Form */}
        {showCreateForm && (
          <div className="border border-gray-200 rounded-lg p-6 bg-gray-50">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Create New Task
            </h2>
            <TaskForm
              onSubmit={handleCreateTask}
              onCancel={() => setShowCreateForm(false)}
              submitLabel="Create Task"
              isLoading={isCreatingTask}
            />
          </div>
        )}

        {/* Tasks List */}
        <div>
          {tasks.length > 0 && (
            <div className="mb-4">
              <p className="text-sm text-gray-500">
                Showing {tasks.length} task{tasks.length !== 1 ? 's' : ''}
              </p>
            </div>
          )}

          <TaskList
            tasks={tasks}
            onEdit={handleEditTask}
            onDelete={handleDeleteTask}
            onLoadMore={handleLoadMore}
            hasMore={hasMore}
            isLoading={isLoading}
            emptyMessage="No tasks found. Create your first task to get started!"
          />
        </div>
      </VerticalStackLayout>
    </div>
  );
};

export default TasksPage;
