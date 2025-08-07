import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

import { useAccountContext } from 'frontend/contexts';
import TaskService from 'frontend/services/task.service';
import { TaskModel } from 'frontend/types/task';
import TaskCard from 'frontend/components/task/task-card.component';
import TaskForm from 'frontend/components/task/task-form.component';

const TasksPage: React.FC = () => {
  const { account } = useAccountContext();
  const [tasks, setTasks] = useState<TaskModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskModel | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deletingTaskId, setDeletingTaskId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const taskService = new TaskService();

  const loadTasks = async (page = 1) => {
    if (!account) return;

    try {
      setLoading(true);
      const result = await taskService.getTasks(account.id, { page, size: 10 });
      setTasks(result.items);
      setTotalCount(result.totalCount);
      setTotalPages(Math.ceil(result.totalCount / 10));
      setCurrentPage(page);
    } catch (error) {
      console.error('Error loading tasks:', error);
      toast.error('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (account) {
      loadTasks();
    }
  }, [account]);

  const handleCreateTask = async (taskData: { title: string; description: string }) => {
    if (!account) return;

    try {
      setIsSubmitting(true);
      await taskService.createTask(account.id, taskData);
      toast.success('Task created successfully');
      setShowForm(false);
      loadTasks(currentPage);
    } catch (error) {
      console.error('Error creating task:', error);
      toast.error('Failed to create task');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateTask = async (taskData: { title: string; description: string }) => {
    if (!account || !editingTask) return;

    try {
      setIsSubmitting(true);
      await taskService.updateTask(account.id, editingTask.id, taskData);
      toast.success('Task updated successfully');
      setEditingTask(null);
      loadTasks(currentPage);
    } catch (error) {
      console.error('Error updating task:', error);
      toast.error('Failed to update task');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!account) return;

    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      setDeletingTaskId(taskId);
      await taskService.deleteTask(account.id, taskId);
      toast.success('Task deleted successfully');
      loadTasks(currentPage);
    } catch (error) {
      console.error('Error deleting task:', error);
      toast.error('Failed to delete task');
    } finally {
      setDeletingTaskId(null);
    }
  };

  const handleEditTask = (task: TaskModel) => {
    setEditingTask(task);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTask(null);
  };

  const handlePageChange = (page: number) => {
    loadTasks(page);
  };

  if (!account) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading account...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            <svg className="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Task
          </button>
        </div>

        {showForm && (
          <div className="mb-6">
            <TaskForm
              onSubmit={handleCreateTask}
              onCancel={handleCancelForm}
              isLoading={isSubmitting}
            />
          </div>
        )}

        {editingTask && (
          <div className="mb-6">
            <TaskForm
              task={editingTask}
              onSubmit={handleUpdateTask}
              onCancel={handleCancelForm}
              isLoading={isSubmitting}
            />
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-gray-600">Loading tasks...</p>
          </div>
        </div>
      ) : tasks.length === 0 ? (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
          <p className="text-gray-600 mb-4">Get started by creating your first task.</p>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90"
          >
            Create Task
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
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

          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-2">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              
              <span className="px-3 py-2 text-sm text-gray-700">
                Page {currentPage} of {totalPages}
              </span>
              
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}

          <div className="text-center text-sm text-gray-500 mt-4">
            Showing {tasks.length} of {totalCount} tasks
          </div>
        </>
      )}
    </div>
  );
};

export default TasksPage; 