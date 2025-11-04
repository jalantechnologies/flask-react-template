import React, { useState, useEffect } from 'react';
import clsx from 'clsx';

import { Button, TaskItem, VerticalStackLayout, H2 } from 'frontend/components';
import { Task } from 'frontend/types';
import { ButtonType, ButtonKind } from 'frontend/types/button';
import TaskService from 'frontend/services/task.service';

interface DashboardProps {
  currentAccountId: string;
}

const Dashboard: React.FC<DashboardProps> = ({ currentAccountId }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  const taskService = new TaskService();

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await taskService.getTasks(currentAccountId);

      if (response.data) {
        setTasks(response.data.items);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load tasks';
      setError(errorMessage);
      console.error('Error loading tasks:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (currentAccountId) {
      loadTasks();
    }
  }, [currentAccountId]);

  const handleCreateTask = async () => {
    // For now, just create a sample task
    try {
      const response = await taskService.createTask(
        currentAccountId,
        'Sample Task',
        'This is a sample task for demonstration purposes.'
      );

      if (response.data) {
        setTasks(prev => [response.data!, ...prev]);
        setShowCreateForm(false);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create task';
      console.error('Error creating task:', err);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await taskService.deleteTask(currentAccountId, taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete task';
      console.error('Error deleting task:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <VerticalStackLayout gap={8}>
          {/* Header */}
          <div className="flex items-center justify-between">
            <H2>My Tasks</H2>
            <Button
              type={ButtonType.BUTTON}
              kind={ButtonKind.PRIMARY}
              onClick={() => setShowCreateForm(true)}
            >
              Create Task
            </Button>
          </div>

          {/* Create Task Form */}
          {showCreateForm && (
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-medium mb-4">Create New Task</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg p-2"
                    placeholder="Task title"
                    defaultValue="Sample Task"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    className="w-full border border-gray-300 rounded-lg p-2"
                    rows={3}
                    placeholder="Task description"
                    defaultValue="This is a sample task for demonstration purposes."
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    type={ButtonType.BUTTON}
                    kind={ButtonKind.PRIMARY}
                    onClick={handleCreateTask}
                  >
                    Create Task
                  </Button>
                  <Button
                    type={ButtonType.BUTTON}
                    kind={ButtonKind.SECONDARY}
                    onClick={() => setShowCreateForm(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-8">
              <div className="text-gray-500">Loading tasks...</div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="text-red-700">{error}</div>
              <Button
                type={ButtonType.BUTTON}
                kind={ButtonKind.TERTIARY}
                onClick={loadTasks}
                className="mt-2"
              >
                Retry
              </Button>
            </div>
          )}

          {/* Tasks List */}
          {!isLoading && !error && (
            <div className="space-y-6">
              {tasks.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                  <div className="text-gray-500 mb-4">No tasks found</div>
                  <Button
                    type={ButtonType.BUTTON}
                    kind={ButtonKind.PRIMARY}
                    onClick={() => setShowCreateForm(true)}
                  >
                    Create Your First Task
                  </Button>
                </div>
              ) : (
                <VerticalStackLayout gap={6}>
                  {tasks.map((task) => (
                    <TaskItem
                      key={task.id}
                      task={task}
                      currentAccountId={currentAccountId}
                      onDelete={handleDeleteTask}
                    />
                  ))}
                </VerticalStackLayout>
              )}
            </div>
          )}
        </VerticalStackLayout>
      </div>
    </div>
  );
};

export default Dashboard;
