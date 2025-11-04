import React, { useState } from 'react';
import clsx from 'clsx';

import { CommentSection } from 'frontend/components/comment';
import { Button } from 'frontend/components';
import { H2, ParagraphMedium } from 'frontend/components/typography';
import { Task } from 'frontend/types';
import { ButtonType, ButtonKind } from 'frontend/types/button';

interface TaskItemProps {
  task: Task;
  currentAccountId: string;
  onUpdate?: (taskId: string, title: string, description: string) => Promise<void>;
  onDelete?: (taskId: string) => Promise<void>;
  className?: string;
}

const TaskItem: React.FC<TaskItemProps> = ({
  task,
  currentAccountId,
  onUpdate,
  onDelete,
  className,
}) => {
  const [showComments, setShowComments] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const isOwnedByCurrentUser = task.isOwnedBy(currentAccountId);

  const handleToggleComments = () => {
    setShowComments(!showComments);
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        setIsDeleting(true);
        await onDelete?.(task.id);
      } catch (err) {
        console.error('Error deleting task:', err);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <div className={clsx(
      'border border-gray-200 rounded-lg p-6 bg-white shadow-sm',
      className
    )}>
      {/* Task Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <H2 className="mb-2">{task.title}</H2>
          <ParagraphMedium className="text-gray-600">
            {task.description}
          </ParagraphMedium>
        </div>

        {/* Action buttons */}
        <div className="flex gap-2 ml-4">
          {isOwnedByCurrentUser && (
            <Button
              type={ButtonType.BUTTON}
              kind={ButtonKind.TERTIARY}
              onClick={handleDelete}
              isLoading={isDeleting}
              disabled={isDeleting}
              className="text-red-500 hover:text-red-700"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          )}
        </div>
      </div>

      {/* Comments Section */}
      <div className="border-t border-gray-100 pt-4">
        <Button
          type={ButtonType.BUTTON}
          kind={ButtonKind.SECONDARY}
          onClick={handleToggleComments}
          className="w-full text-left justify-start"
        >
          {showComments ? 'Hide Comments' : 'Show Comments'}
        </Button>

        {showComments && (
          <div className="mt-6">
            <CommentSection
              taskId={task.id}
              accountId={task.accountId}
              currentAccountId={currentAccountId}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskItem;