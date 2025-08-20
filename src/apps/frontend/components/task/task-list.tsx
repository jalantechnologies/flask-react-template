import React from 'react';

import Button from 'frontend/components/button';
import VerticalStackLayout from 'frontend/components/layouts/vertical-stack-layout';
import TaskItem from 'frontend/components/task/task-item';
import { ButtonKind, Task, TaskFormData } from 'frontend/types';

interface TaskListProps {
  tasks: Task[];
  onEdit: (taskId: string, data: TaskFormData) => void;
  onDelete: (taskId: string) => void;
  onLoadMore?: () => void;
  hasMore?: boolean;
  isLoading?: boolean;
  emptyMessage?: string;
}

const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onEdit,
  onDelete,
  onLoadMore,
  hasMore = false,
  isLoading = false,
  emptyMessage = 'No tasks found. Create your first task to get started!',
}) => {
  if (tasks.length === 0 && !isLoading) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500 text-lg mb-2">📋</div>
        <p className="text-gray-600">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <VerticalStackLayout gap={4}>
      <div className="grid gap-4">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onEdit={onEdit}
            onDelete={onDelete}
            isLoading={isLoading}
          />
        ))}
      </div>

      {hasMore && onLoadMore && (
        <div className="flex justify-center">
          <Button
            kind={ButtonKind.TERTIARY}
            onClick={onLoadMore}
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : 'Load More'}
          </Button>
        </div>
      )}

      {isLoading && tasks.length === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-500">Loading tasks...</div>
        </div>
      )}
    </VerticalStackLayout>
  );
};

export default TaskList;
