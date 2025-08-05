import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TaskForm } from 'frontend/components';
import { TaskService } from 'frontend/services';
import { useAuthContext } from 'frontend/contexts';
import { Task } from 'frontend/types';

const TaskEdit: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const { accessToken } = useAuthContext();
  const navigate = useNavigate();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTask = async () => {
      if (!taskId) {
        setError('Task ID is missing');
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const taskService = new TaskService();
        const response = await taskService.getTask(accessToken, taskId);
        
        if (response.error) {
          throw new Error(response.error.message);
        }
        
        setTask(response.data as Task);
      } catch (err) {
        setError('Failed to load task details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [accessToken, taskId]);

  const handleSuccess = () => {
    // Redirect to task detail page after successful update
    navigate(`/tasks/${taskId}`);
  };

  if (loading) {
    return <div className="container mx-auto p-4">Loading task...</div>;
  }

  if (error || !task) {
    return (
      <div className="container mx-auto p-4">
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error || 'Task not found'}
        </div>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 text-blue-500 hover:text-blue-700 transition-colors"
        >
          &larr; Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center mb-6">
          <button
            onClick={() => navigate(`/tasks/${taskId}`)}
            className="mr-4 text-blue-500 hover:text-blue-700 transition-colors"
          >
            &larr; Back to Task
          </button>
          <h1 className="text-2xl font-bold">Edit Task</h1>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <TaskForm
            accessToken={accessToken}
            taskId={taskId}
            initialTitle={task.title}
            initialDescription={task.description}
            onSuccess={handleSuccess}
            onCancel={() => navigate(`/tasks/${taskId}`)}
            submitLabel="Update Task"
          />
        </div>
      </div>
    </div>
  );
};

export default TaskEdit;