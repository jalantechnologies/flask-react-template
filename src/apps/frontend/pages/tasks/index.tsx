import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

import { TaskService } from 'frontend/services';
import {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  TasksListResponse,
} from 'frontend/types';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';
import TaskList from './task-list';
import TaskForm from './task-form';
import TaskModal from './task-modal';

interface TasksState {
  tasks: Task[];
  loading: boolean;
  creating: boolean;
  updating: boolean;
  deleting: string | null;
  editingTask: Task | null;
  showCreateForm: boolean;
  showEditModal: boolean;
  pagination: {
    page: number;
    size: number;
    total: number;
    hasMore: boolean;
  };
}

const Tasks: React.FC = () => {
  const taskService = new TaskService();

  const [state, setState] = useState<TasksState>({
    tasks: [],
    loading: true,
    creating: false,
    updating: false,
    deleting: null,
    editingTask: null,
    showCreateForm: false,
    showEditModal: false,
    pagination: {
      page: 1,
      size: 10,
      total: 0,
      hasMore: false,
    },
  });

  const loadTasks = async (page: number = 1, size: number = 10) => {
    const userAccessToken = getAccessTokenFromStorage();
    if (!userAccessToken) return;

    setState(prev => ({ ...prev, loading: true }));

    try {
      const response = await taskService.getTasks(userAccessToken, { page, size });
      const tasksData = response.data as TasksListResponse;
      const tasks = tasksData.items.map(item => new Task(item as any));

      setState(prev => ({
        ...prev,
        tasks,
        loading: false,
        pagination: {
          page: tasksData.page,
          size: tasksData.size,
          total: tasksData.total,
          hasMore: tasksData.has_more,
        },
      }));
    } catch (error: any) {
      toast.error(error.message || 'Failed to load tasks');
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  const handleCreateTask = async (taskData: CreateTaskRequest) => {
    const userAccessToken = getAccessTokenFromStorage();
    if (!userAccessToken) return;

    setState(prev => ({ ...prev, creating: true }));

    try {
      const response = await taskService.createTask(userAccessToken, taskData);
      const newTask = new Task(response.data as any);
      
      setState(prev => ({
        ...prev,
        tasks: [newTask, ...prev.tasks],
        creating: false,
        showCreateForm: false,
        pagination: {
          ...prev.pagination,
          total: prev.pagination.total + 1,
        },
      }));
      
      toast.success('Task created successfully!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to create task');
      setState(prev => ({ ...prev, creating: false }));
    }
  };

  const handleUpdateTask = async (taskId: string, taskData: UpdateTaskRequest) => {
    const userAccessToken = getAccessTokenFromStorage();
    if (!userAccessToken) return;

    setState(prev => ({ ...prev, updating: true }));

    try {
      const response = await taskService.updateTask(userAccessToken, taskId, taskData);
      const updatedTask = new Task(response.data as any);
      
      setState(prev => ({
        ...prev,
        tasks: prev.tasks.map(task => task.id === taskId ? updatedTask : task),
        updating: false,
        editingTask: null,
        showEditModal: false,
      }));
      
      toast.success('Task updated successfully!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to update task');
      setState(prev => ({ ...prev, updating: false }));
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    const userAccessToken = getAccessTokenFromStorage();
    if (!userAccessToken || !confirm('Are you sure you want to delete this task?')) return;

    setState(prev => ({ ...prev, deleting: taskId }));

    try {
      await taskService.deleteTask(userAccessToken, taskId);
      
      setState(prev => ({
        ...prev,
        tasks: prev.tasks.filter(task => task.id !== taskId),
        deleting: null,
        pagination: {
          ...prev.pagination,
          total: Math.max(0, prev.pagination.total - 1),
        },
      }));
      
      toast.success('Task deleted successfully!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete task');
      setState(prev => ({ ...prev, deleting: null }));
    }
  };

  const openEditModal = (task: Task) => {
    setState(prev => ({
      ...prev,
      editingTask: task,
      showEditModal: true,
    }));
  };

  const closeEditModal = () => {
    setState(prev => ({
      ...prev,
      editingTask: null,
      showEditModal: false,
    }));
  };

  const toggleCreateForm = () => {
    setState(prev => ({ ...prev, showCreateForm: !prev.showCreateForm }));
  };

  const loadMoreTasks = () => {
    if (state.pagination.hasMore) {
      loadTasks(state.pagination.page + 1, state.pagination.size);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  return (
    <div className="tasks-page">
      <div className="tasks-header">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Tasks</h1>
        <button
          onClick={toggleCreateForm}
          className="bg-orange-600 hover:bg-orange-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {state.showCreateForm ? 'Cancel' : 'Create Task'}
        </button>
      </div>

      {state.showCreateForm && (
        <div className="mb-8">
          <TaskForm
            onSubmit={handleCreateTask}
            loading={state.creating}
            onCancel={toggleCreateForm}
          />
        </div>
      )}

      <TaskList
        tasks={state.tasks}
        loading={state.loading}
        deleting={state.deleting}
        onEdit={openEditModal}
        onDelete={handleDeleteTask}
        pagination={state.pagination}
        onLoadMore={loadMoreTasks}
      />

      {state.showEditModal && state.editingTask && (
        <TaskModal
          task={state.editingTask}
          onSubmit={(taskData) => handleUpdateTask(state.editingTask!.id, taskData)}
          loading={state.updating}
          onClose={closeEditModal}
        />
      )}
    </div>
  );
};

export default Tasks;