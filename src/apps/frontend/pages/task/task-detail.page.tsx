import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { CommentList } from 'frontend/components';
import { TaskService } from 'frontend/services';
import { AccessToken } from 'frontend/types';
import { Task } from 'frontend/services/task.service';

interface TaskDetailProps {
  accessToken: AccessToken;
}

// Task interface is imported from task.service.ts

const TaskDetail: React.FC<TaskDetailProps> = ({ accessToken }) => {
  const { taskId } = useParams<{ taskId: string }>();
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

  if (loading) {
    return <div className="p-6">Loading task details...</div>;
  }

  if (error || !task) {
    return (
      <div className="p-6">
        <div className="p-4 bg-red-100 text-red-700 rounded mb-4">
          {error || 'Task not found'}
        </div>
        <button
          onClick={() => navigate(-1)}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Go Back
        </button>
      </div>
    );
  }

  const handleDeleteTask = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      const taskService = new TaskService();
      const response = await taskService.deleteTask(accessToken, task.id);
      
      if (response.error) {
        throw new Error(response.error.message);
      }
      
      // Redirect to dashboard after successful deletion
      navigate('/');
    } catch (err) {
      setError('Failed to delete task');
      console.error(err);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <button
          onClick={() => navigate(-1)}
          className="text-blue-500 hover:text-blue-700 transition-colors"
        >
          &larr; Back to Dashboard
        </button>
        <div className="flex space-x-2">
          <Link
            to={`/tasks/${task.id}/edit`}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Edit Task
          </Link>
          <button
            onClick={handleDeleteTask}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            Delete Task
          </button>
        </div>
      </div>

      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">{task.title}</h1>
        <p className="text-gray-700 whitespace-pre-wrap mb-4">{task.description}</p>
      </div>

      <hr className="my-6" />

      {/* Comments Section */}
      {taskId && (
        <CommentList accessToken={accessToken} taskId={taskId} />
      )}
    </div>
  );
};

export default TaskDetail;