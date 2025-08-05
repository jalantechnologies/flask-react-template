import React, { useState, useEffect } from 'react';

import Button from 'frontend/components/button';
import TaskCard from 'frontend/components/task-card';
import TaskForm from 'frontend/components/task-form';
import VerticalStackLayout from 'frontend/components/layouts/vertical-stack-layout';
import H2 from 'frontend/components/typography/h2';
import ParagraphMedium from 'frontend/components/typography/paragraph-medium';
import TaskService from 'frontend/services/task.service';
import { ButtonKind } from 'frontend/types/button';
import {
  CreateTaskRequest,
  PaginatedTasksResponse,
  Task,
  UpdateTaskRequest,
} from 'frontend/types/task';

const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | undefined>();
  const [formLoading, setFormLoading] = useState(false);
  const [deletingTaskId, setDeletingTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Mock account ID - in a real app, this would come from auth context
  const accountId = 'mock-account-id';

  const taskService = new TaskService();

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await taskService.getTasks(accountId);
      const data = response.data as PaginatedTasksResponse;
      setTasks(data.items);
    } catch (err) {
      setError('Failed to load tasks. Please try again.');
      console.error('Error loading tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadTasks();
  }, []);

  const handleCreateTask = async (taskData: CreateTaskRequest) => {
    try {
      setFormLoading(true);
      setError(null);
      await taskService.createTask(accountId, taskData);
      setShowForm(false);
      await loadTasks();
    } catch (err) {
      setError('Failed to create task. Please try again.');
      console.error('Error creating task:', err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleUpdateTask = async (taskData: UpdateTaskRequest) => {
    if (!editingTask) return;

    try {
      setFormLoading(true);
      setError(null);
      await taskService.updateTask(accountId, editingTask.id, taskData);
      setShowForm(false);
      setEditingTask(undefined);
      await loadTasks();
    } catch (err) {
      setError('Failed to update task. Please try again.');
      console.error('Error updating task:', err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      setDeletingTaskId(taskId);
      setError(null);
      await taskService.deleteTask(accountId, taskId);
      await loadTasks();
    } catch (err) {
      setError('Failed to delete task. Please try again.');
      console.error('Error deleting task:', err);
    } finally {
      setDeletingTaskId(null);
    }
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTask(undefined);
    setError(null);
  };

  const handleSubmitForm = (data: CreateTaskRequest | UpdateTaskRequest) => {
    if (editingTask) {
      void handleUpdateTask(data as UpdateTaskRequest);
    } else {
      void handleCreateTask(data as CreateTaskRequest);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <ParagraphMedium>Loading tasks...</ParagraphMedium>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <VerticalStackLayout gap={6}>
        <div className="flex items-center justify-between">
          <H2>Task Management</H2>
          <Button
            kind={ButtonKind.PRIMARY}
            onClick={() => setShowForm(true)}
            disabled={showForm}
          >
            Add New Task
          </Button>
        </div>

        {error && (
          <div className="rounded-lg bg-red-50 border border-red-200 p-4">
            <ParagraphMedium>
              Failed to load tasks. Please try again.
            </ParagraphMedium>
          </div>
        )}

        {showForm && (
          <div className="rounded-lg border border-stroke bg-white p-6">
            <H2>{editingTask ? 'Edit Task' : 'Create New Task'}</H2>
            <div className="mt-4">
              <TaskForm
                task={editingTask}
                onSubmit={handleSubmitForm}
                onCancel={handleCancelForm}
                isLoading={formLoading}
              />
            </div>
          </div>
        )}

        {tasks.length === 0 && !showForm ? (
          <div className="text-center py-12">
            <ParagraphMedium>
              No tasks found. Create your first task to get started!
            </ParagraphMedium>
            <div className="mt-4">
              <Button
                kind={ButtonKind.PRIMARY}
                onClick={() => setShowForm(true)}
              >
                Create Your First Task
              </Button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onEdit={handleEditTask}
                onDelete={handleDeleteTask}
                isDeleting={deletingTaskId === task.id}
              />
            ))}
          </div>
        )}
      </VerticalStackLayout>
    </div>
  );
};

export default TasksPage;
