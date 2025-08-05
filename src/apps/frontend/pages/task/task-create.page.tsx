import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TaskForm } from 'frontend/components';
import { useAuthContext } from 'frontend/contexts';

const TaskCreate: React.FC = () => {
  const { accessToken } = useAuthContext();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const handleSuccess = () => {
    // Redirect to dashboard after successful task creation
    navigate('/');
  };

  return (
    <div className="container mx-auto p-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center mb-6">
          <button
            onClick={() => navigate('/')}
            className="mr-4 text-blue-500 hover:text-blue-700 transition-colors"
          >
            &larr; Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold">Create New Task</h1>
        </div>

        {error && (
          <div className="p-3 mb-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <div className="bg-white p-6 rounded-lg shadow-md">
          <TaskForm
            accessToken={accessToken}
            onSuccess={handleSuccess}
            onCancel={() => navigate('/')}
            submitLabel="Create Task"
          />
        </div>
      </div>
    </div>
  );
};

export default TaskCreate;