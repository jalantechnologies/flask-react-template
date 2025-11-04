import React, { useState, useEffect } from 'react';
import clsx from 'clsx';

import { Button, TaskForm, TaskList, VerticalStackLayout, H2 } from 'frontend/components';
import { Task, TaskFormData } from 'frontend/types';
import { ButtonType, ButtonKind } from 'frontend/types/button';
import TaskService from 'frontend/services/task.service';

interface DashboardProps {
  currentAccountId: string;
}

const Dashboard: React.FC<DashboardProps> = ({ currentAccountId }) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0); // For refreshing task list

  const taskService = new TaskService();

  const handleCreateTask = async (data: TaskFormData) => {
    try {
      setIsCreating(true);
      setCreateError(null);

      const response = await taskService.createTask(
        currentAccountId,
        data.title,
        data.description
      );

      if (response.data) {
        setShowCreateForm(false);
        // Refresh the task list
        setRefreshKey(prev => prev + 1);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create task';
      setCreateError(errorMessage);
      console.error('Error creating task:', err);
      throw err; // Re-throw to let the form handle it
    } finally {
      setIsCreating(false);
    }
  };

  const handleTaskUpdate = (taskId: string, updatedTask: Task) => {
    // Task list component will handle the update
    console.log('Task updated:', taskId, updatedTask);
  };

  const handleTaskDelete = (taskId: string) => {
    // Task list component will handle the deletion
    console.log('Task deleted:', taskId);
  };

  const handleCancelCreate = () => {
    setShowCreateForm(false);
    setCreateError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <VerticalStackLayout gap={8}>
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <H2>Task Management Dashboard</H2>
              <p className="text-gray-600 mt-1">
                Manage your tasks efficiently with full CRUD operations
              </p>
            </div>
            <Button
              type={ButtonType.BUTTON}
              kind={ButtonKind.PRIMARY}
              onClick={() => setShowCreateForm(true)}
            >
              Create New Task
            </Button>
          </div>

          {/* Create Task Form */}
          {showCreateForm && (
            <TaskForm
              onSubmit={handleCreateTask}
              onCancel={handleCancelCreate}
              isSubmitting={isCreating}
              submitButtonText="Create Task"
              showCancelButton={true}
              title="Create New Task"
              autoFocus={true}
              errors={createError ? { general: createError } : undefined}
            />
          )}

          {/* Task Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                  <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Tasks</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {/* This will be populated by the task list component */}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Tasks</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {/* This will be populated by the task list component */}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
                  <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Recently Updated</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {/* This will be populated by the task list component */}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Task List - Takes up 2/3 of the space */}
            <div className="lg:col-span-2">
              <TaskList
                key={refreshKey} // This forces re-render when tasks change
                accountId={currentAccountId}
                currentAccountId={currentAccountId}
                onTaskUpdate={handleTaskUpdate}
                onTaskDelete={handleTaskDelete}
                showSearch={true}
                showFilters={true}
                pageSize={10}
              />
            </div>

            {/* Sidebar - Takes up 1/3 of the space */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-medium mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <Button
                    type={ButtonType.BUTTON}
                    kind={ButtonKind.SECONDARY}
                    onClick={() => setShowCreateForm(true)}
                    className="w-full"
                  >
                    Create Task
                  </Button>
                  <Button
                    type={ButtonType.BUTTON}
                    kind={ButtonKind.TERTIARY}
                    onClick={() => setRefreshKey(prev => prev + 1)}
                    className="w-full"
                  >
                    Refresh Tasks
                  </Button>
                </div>
              </div>

              {/* Tips */}
              <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
                <h3 className="text-lg font-medium mb-4 text-blue-900">
                  💡 Pro Tips
                </h3>
                <ul className="space-y-2 text-sm text-blue-800">
                  <li>• Use descriptive titles for better organization</li>
                  <li>• Add detailed descriptions to provide context</li>
                  <li>• Comments help collaborate on tasks</li>
                  <li>• Search and filter to find specific tasks quickly</li>
                  <li>• Edit tasks to keep information up-to-date</li>
                </ul>
              </div>

              {/* Recent Activity */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-medium mb-4">Recent Activity</h3>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0 h-2 w-2 bg-green-500 rounded-full"></div>
                    <p className="text-sm text-gray-600">System ready</p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0 h-2 w-2 bg-blue-500 rounded-full"></div>
                    <p className="text-sm text-gray-600">Tasks loaded</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </VerticalStackLayout>
      </div>
    </div>
  );
};

export default Dashboard;
