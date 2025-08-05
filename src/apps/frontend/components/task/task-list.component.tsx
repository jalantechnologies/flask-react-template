import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { TaskService } from 'frontend/services';
import { AccessToken, Task } from 'frontend/types';

interface TaskListProps {
  accessToken: AccessToken;
}

const TaskList: React.FC<TaskListProps> = ({ accessToken }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [pageSize] = useState<number>(10);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const taskService = new TaskService();
      const response = await taskService.getPaginatedTasks(accessToken, page, pageSize);
      
      if (response.error) {
        throw new Error(response.error.message);
      }
      
      setTasks(response.data?.items || []);
      setTotalPages(response.data?.total_pages || 1);
    } catch (err) {
      setError('Failed to load tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [accessToken, page, pageSize]);

  const handlePreviousPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };

  const handleNextPage = () => {
    if (page < totalPages) {
      setPage(page + 1);
    }
  };

  if (loading) {
    return <div className="p-4">Loading tasks...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Your Tasks</h2>
      
      {tasks.length === 0 ? (
        <p>No tasks found. Create a new task to get started.</p>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <div key={task.id} className="border p-4 rounded shadow-sm hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold">{task.title}</h3>
              <p className="text-gray-600 line-clamp-2">{task.description}</p>
              <div className="mt-2">
                <Link 
                  to={`/tasks/${task.id}`} 
                  className="text-blue-500 hover:text-blue-700 transition-colors"
                >
                  View Details
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {tasks.length > 0 && (
        <div className="flex justify-between items-center mt-4">
          <button 
            onClick={handlePreviousPage} 
            disabled={page === 1}
            className={`px-4 py-2 rounded ${page === 1 ? 'bg-gray-300 cursor-not-allowed' : 'bg-blue-500 text-white hover:bg-blue-600'}`}
          >
            Previous
          </button>
          <span>Page {page} of {totalPages}</span>
          <button 
            onClick={handleNextPage} 
            disabled={page === totalPages}
            className={`px-4 py-2 rounded ${page === totalPages ? 'bg-gray-300 cursor-not-allowed' : 'bg-blue-500 text-white hover:bg-blue-600'}`}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default TaskList;