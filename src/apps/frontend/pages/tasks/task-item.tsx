import React from 'react';

import { Task } from 'frontend/types';

interface TaskItemProps {
  task: Task;
  isDeleting: boolean;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, isDeleting, onEdit, onDelete }) => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-medium text-gray-900 truncate">
            {task.title}
          </h3>
          <p className="text-gray-600 mt-1 line-clamp-2">
            {task.description}
          </p>
          <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
            <span>
              Created: {task.displayCreatedAt()}
            </span>
            <span>
              Updated: {task.displayUpdatedAt()}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 ml-4">
          <button
            onClick={() => onEdit(task)}
            disabled={isDeleting}
            className="text-orange-600 hover:text-orange-800 disabled:text-gray-400 transition-colors p-2"
            title="Edit task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          
          <button
            onClick={() => onDelete(task.id)}
            disabled={isDeleting}
            className="text-red-600 hover:text-red-800 disabled:text-gray-400 transition-colors p-2"
            title="Delete task"
          >
            {isDeleting ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskItem;