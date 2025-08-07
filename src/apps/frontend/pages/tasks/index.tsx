import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

import { 
  Button, 
  H2, 
  VerticalStackLayout 
} from 'frontend/components';
import TaskList from 'frontend/pages/tasks/components/task-list';
import TaskForm from 'frontend/pages/tasks/components/task-form';
import TaskService from 'frontend/services/task-service';
import { ButtonKind, ButtonType } from 'frontend/types/button';
import { AsyncError } from 'frontend/types';
import { Task } from 'frontend/types/task';
import { useAccountContext } from 'frontend/contexts';

interface TasksPageState {
  tasks: Task[];
  isLoading: boolean;
  showForm: boolean;
  editingTask: Task | null;
  isSubmitting: boolean;
}

const TasksPage: React.FC = () => {
  const { accountDetails } = useAccountContext();
  const [state, setState] = useState<TasksPageState>({
    tasks: [],
    isLoading: false,
    showForm: false,
    editingTask: null,
    isSubmitting: false,
  });

  const taskService = new TaskService();

  // Load tasks
  const loadTasks = async () => {
    setState(prev => ({ ...prev, isLoading: true }));
    try {
      const response = await taskService.getTasks(accountDetails.id, 1, 50);
      if (response.data) {
        setState(prev => ({ ...prev, tasks: response.data!.items, isLoading: false }));
      }
    } catch (error) {
      const asyncError = error as AsyncError;
      toast.error(asyncError.message || 'Failed to load tasks');
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  // Load tasks on component mount
  useEffect(() => {
    loadTasks();
  }, [accountDetails.id]);

  // Handle create new task
  const handleCreateTask = () => {
    setState(prev => ({ 
      ...prev, 
      showForm: true, 
      editingTask: null 
    }));
  };

  // Handle edit task
  const handleEditTask = (task: Task) => {
    setState(prev => ({ 
      ...prev, 
      showForm: true, 
      editingTask: task 
    }));
  };

  // Handle delete task
  const handleDeleteTask = async (taskId: string) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await taskService.deleteTask(accountDetails.id, taskId);
      toast.success('Task deleted successfully');
      await loadTasks(); // Reload tasks
    } catch (error) {
      const asyncError = error as AsyncError;
      toast.error(asyncError.message || 'Failed to delete task');
    }
  };

  // Handle form submission (create or update)
  const handleFormSubmit = async (taskData: { title: string; description: string }) => {
    setState(prev => ({ ...prev, isSubmitting: true }));
    try {
      if (state.editingTask) {
        // Update existing task
        await taskService.updateTask(accountDetails.id, state.editingTask.id, taskData);
        toast.success('Task updated successfully');
      } else {
        // Create new task
        await taskService.createTask(accountDetails.id, taskData);
        toast.success('Task created successfully');
      }
      
      setState(prev => ({ 
        ...prev, 
        showForm: false, 
        editingTask: null, 
        isSubmitting: false 
      }));
      await loadTasks(); // Reload tasks
    } catch (error) {
      const asyncError = error as AsyncError;
      toast.error(asyncError.message || 'Failed to save task');
      setState(prev => ({ ...prev, isSubmitting: false }));
    }
  };

  // Handle form cancel
  const handleFormCancel = () => {
    setState(prev => ({ 
      ...prev, 
      showForm: false, 
      editingTask: null 
    }));
  };

  if (state.showForm) {
    return (
      <div className="p-6">
        <TaskForm
          task={state.editingTask}
          onSubmit={handleFormSubmit}
          onCancel={handleFormCancel}
          isLoading={state.isSubmitting}
        />
      </div>
    );
  }

  return (
    <div className="p-6">
      <VerticalStackLayout gap={6}>
        <div className="flex items-center justify-between">
          <H2>Tasks</H2>
          <Button
            type={ButtonType.BUTTON}
            kind={ButtonKind.PRIMARY}
            onClick={handleCreateTask}
          >
            Create New Task
          </Button>
        </div>

        {state.isLoading ? (
          <div className="rounded-sm border border-stroke bg-white px-5 py-6 shadow-default dark:border-strokedark dark:bg-boxdark">
            <div className="text-center">
              <p>Loading tasks...</p>
            </div>
          </div>
        ) : (
          <TaskList
            tasks={state.tasks}
            onEdit={handleEditTask}
            onDelete={handleDeleteTask}
          />
        )}
      </VerticalStackLayout>
    </div>
  );
};

export default TasksPage;
