import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

import { TaskList, TaskForm } from './components';
import { Task, AsyncError } from 'frontend/types';
import { TaskService } from 'frontend/services';
import { useAuth } from 'frontend/contexts/auth.provider';
import { VerticalStackLayout, H2, Button } from 'frontend/components';
import { ButtonKind } from 'frontend/types/button';
import routes from 'frontend/constants/routes';

export const Tasks: React.FC = () => {
  const navigate = useNavigate();
  const { userAccessToken } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadTasks = async () => {
    if (!userAccessToken) {
      navigate(routes.LOGIN);
      return;
    }

    try {
      setLoading(true);
      const response = await TaskService.getTasks(userAccessToken, currentPage, 10);
      setTasks(response.data.items);
      setTotalPages(Math.ceil(response.data.total_count / 10));
    } catch (error) {
      const asyncError = error as AsyncError;
      toast.error(asyncError.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [currentPage, userAccessToken]);

  const handleCreateTask = async (taskData: { title: string; description: string }) => {
    if (!userAccessToken) return;

    try {
      await TaskService.createTask(userAccessToken, taskData);
      toast.success('Task created successfully');
      setShowCreateForm(false);
      loadTasks();
    } catch (error) {
      const asyncError = error as AsyncError;
      toast.error(asyncError.message || 'Failed to create task');
    }
  };

  const handleUpdateTask = async (taskData: { title: string; description: string }) => {
    if (!userAccessToken || !editingTask) return;

    try {
      await TaskService.updateTask(userAccessToken, editingTask.id, taskData);
      toast.success('Task updated successfully');
      setEditingTask(null);
      loadTasks();
    } catch (error) {
      const asyncError = error as AsyncError;
      toast.error(asyncError.message || 'Failed to update task');
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!userAccessToken) return;

    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await TaskService.deleteTask(userAccessToken, taskId);
      toast.success('Task deleted successfully');
      loadTasks();
    } catch (error) {
      const asyncError = error as AsyncError;
      toast.error(asyncError.message || 'Failed to delete task');
    }
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
  };

  const handleCancelEdit = () => {
    setEditingTask(null);
  };

  if (!userAccessToken) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <VerticalStackLayout spacing="large">
        <div className="flex justify-between items-center">
          <H2>Tasks</H2>
          <Button
            onClick={() => setShowCreateForm(true)}
            kind={ButtonKind.PRIMARY}
          >
            Create Task
          </Button>
        </div>

        {showCreateForm && (
          <TaskForm
            onSubmit={handleCreateTask}
            onCancel={() => setShowCreateForm(false)}
            title="Create New Task"
          />
        )}

        {editingTask && (
          <TaskForm
            onSubmit={handleUpdateTask}
            onCancel={handleCancelEdit}
            title="Edit Task"
            initialData={{
              title: editingTask.title,
              description: editingTask.description,
            }}
          />
        )}

        <TaskList
          tasks={tasks}
          loading={loading}
          onEdit={handleEditTask}
          onDelete={handleDeleteTask}
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
        />
      </VerticalStackLayout>
    </div>
  );
};

export default Tasks; 