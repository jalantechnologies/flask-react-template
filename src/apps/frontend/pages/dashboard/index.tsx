import React from 'react';
import { Link } from 'react-router-dom';
import { TaskList, TaskForm } from 'frontend/components';
import { useAuthContext } from 'frontend/contexts';

const Dashboard = () => {
  const { accessToken } = useAuthContext();
  const [showTaskForm, setShowTaskForm] = React.useState(false);
  const [refreshKey, setRefreshKey] = React.useState(0);

  const handleTaskSuccess = () => {
    setShowTaskForm(false);
    setRefreshKey(prev => prev + 1); // Trigger a refresh of the task list
  };

  return (
    <div className="container mx-auto p-4" role="main">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowTaskForm(!showTaskForm)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            {showTaskForm ? 'Cancel' : 'Quick Add Task'}
          </button>
          <Link
            to="/tasks/create"
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
          >
            Create Task
          </Link>
        </div>
      </div>

      {showTaskForm && (
        <div className="mb-6 p-4 border rounded shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Create New Task</h2>
          <TaskForm 
            accessToken={accessToken} 
            onSuccess={handleTaskSuccess} 
            onCancel={() => setShowTaskForm(false)}
            submitLabel="Create Task"
          />
        </div>
      )}

      {/* Key prop forces re-render when a task is created or updated */}
      <TaskList key={refreshKey} accessToken={accessToken} />
    </div>
  );
};

export default Dashboard;
