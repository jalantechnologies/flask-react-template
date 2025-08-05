import React, { useState } from 'react';
import { TaskService } from 'frontend/services';
import { AccessToken } from 'frontend/types';

interface TaskFormProps {
  accessToken: AccessToken;
  taskId?: string;
  initialTitle?: string;
  initialDescription?: string;
  onSuccess: () => void;
  onCancel?: () => void;
  submitLabel?: string;
}

const TaskForm: React.FC<TaskFormProps> = ({
  accessToken,
  taskId,
  initialTitle = '',
  initialDescription = '',
  onSuccess,
  onCancel,
  submitLabel = 'Submit',
}) => {
  const [title, setTitle] = useState<string>(initialTitle);
  const [description, setDescription] = useState<string>(initialDescription);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const taskService = new TaskService();
      
      if (taskId) {
        // Update existing task
        const response = await taskService.updateTask(
          accessToken,
          taskId,
          title,
          description
        );
        
        if (response.error) {
          throw new Error(response.error.message);
        }
      } else {
        // Create new task
        const response = await taskService.createTask(
          accessToken,
          title,
          description
        );
        
        if (response.error) {
          throw new Error(response.error.message);
        }
      }
      
      // Clear form and notify parent of success
      setTitle('');
      setDescription('');
      onSuccess();
    } catch (err) {
      setError(`Failed to ${taskId ? 'update' : 'create'} task: ${err instanceof Error ? err.message : 'Unknown error'}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Task title"
          required
        />
      </div>
      
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Task description"
        />
      </div>
      
      <div className="flex justify-end space-x-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={loading}
          >
            Cancel
          </button>
        )}
        
        <button
          type="submit"
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          disabled={loading}
        >
          {loading ? 'Submitting...' : submitLabel}
        </button>
      </div>
    </form>
  );
};

export default TaskForm;