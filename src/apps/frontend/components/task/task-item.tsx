import React, { useState } from 'react';

import Button from 'frontend/components/button';
import HorizontalStackLayout from 'frontend/components/layouts/horizontal-stack-layout';
import VerticalStackLayout from 'frontend/components/layouts/vertical-stack-layout';
import TaskForm from 'frontend/components/task/task-form';
import CommentList from 'frontend/components/task/comment-list';
import { ButtonKind, Task, TaskFormData } from 'frontend/types';

interface TaskItemProps {
  task: Task;
  onEdit: (taskId: string, data: TaskFormData) => void;
  onDelete: (taskId: string) => void;
  isLoading?: boolean;
}

const TaskItem: React.FC<TaskItemProps> = ({
  task,
  onEdit,
  onDelete,
  isLoading = false,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [showComments, setShowComments] = useState(false);

  const handleEdit = (data: TaskFormData) => {
    onEdit(task.id, data);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      onDelete(task.id);
    }
  };

  if (isEditing) {
    return (
      <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Edit Task</h4>
        <TaskForm
          initialData={{
            title: task.title,
            description: task.description,
          }}
          onSubmit={handleEdit}
          onCancel={handleCancelEdit}
          submitLabel="Update Task"
          isLoading={isLoading}
        />
      </div>
    );
  }

  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-sm transition-shadow">
      <VerticalStackLayout gap={3}>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{task.title}</h3>
          <p className="text-gray-600 mt-1">{task.description}</p>
        </div>

        <HorizontalStackLayout gap={2}>
          <Button
            kind={ButtonKind.TERTIARY}
            onClick={() => setShowComments(!showComments)}
            disabled={isLoading}
          >
            {showComments ? 'Hide Comments' : 'Show Comments'}
          </Button>
          <Button
            kind={ButtonKind.TERTIARY}
            onClick={() => setIsEditing(true)}
            disabled={isLoading}
          >
            Edit
          </Button>
          <Button
            kind={ButtonKind.TERTIARY}
            onClick={handleDelete}
            disabled={isLoading}
          >
            Delete
          </Button>
        </HorizontalStackLayout>

        {showComments && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <CommentList taskId={task.id} />
          </div>
        )}
      </VerticalStackLayout>
    </div>
  );
};

export default TaskItem;
