import React from 'react';

import { Task } from 'frontend/types';
import TaskItem from './task-item';

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  deleting: string | null;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
  pagination: {
    page: number;
    size: number;
    total: number;
    hasMore: boolean;
  };
  onLoadMore: () => void;
}

const TaskList: React.FC<TaskListProps> = ({
  tasks,
  loading,
  deleting,
  onEdit,
  onDelete,
  pagination,
  onLoadMore,
}) => {
  if (loading && tasks.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
        <span className="ml-2 text-gray-600">Loading tasks...</span>
      </div>
    );
  }

  if (!loading && tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
        <p className="text-gray-600">Create your first task to get started!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-medium text-gray-900">
          Tasks ({pagination.total})
        </h2>
      </div>

      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            isDeleting={deleting === task.id}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </div>

      {pagination.hasMore && (
        <div className="flex justify-center pt-6">
          <button
            onClick={onLoadMore}
            disabled={loading}
            className="bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 text-gray-700 font-medium py-2 px-6 rounded-lg transition-colors"
          >
            {loading ? 'Loading...' : 'Load More Tasks'}
          </button>
        </div>
      )}

      {!pagination.hasMore && tasks.length > 0 && (
        <div className="text-center pt-6">
          <p className="text-sm text-gray-500">No more tasks to load</p>
        </div>
      )}
    </div>
  );
};

export default TaskList;