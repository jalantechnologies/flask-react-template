import React, { useState } from 'react';
import clsx from 'clsx';

import { CommentSection, Button } from 'frontend/components';
import { H2, ParagraphMedium } from 'frontend/components/typography';
import { Task, TaskFormData, TaskValidationError } from 'frontend/types';
import { ButtonType, ButtonKind } from 'frontend/types/button';
import TaskForm from './task-form.component';

interface TaskItemProps {
  task: Task;
  currentAccountId: string;
  onUpdate?: (taskId: string, task: Task) => void;
  onDelete?: (taskId: string) => void;
  className?: string;
  showComments?: boolean;
}

const TaskItem: React.FC<TaskItemProps> = ({
  task,
  currentAccountId,
  onUpdate,
  onDelete,
  className,
  showComments = true,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [showCommentsSection, setShowCommentsSection] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateError, setUpdateError] = useState<TaskValidationError | null>(null);

  const isOwnedByCurrentUser = task.isOwnedBy(currentAccountId);

  const handleEdit = () => {
    setIsEditing(true);
    setUpdateError(null);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setUpdateError(null);
  };

  const handleUpdate = async (data: TaskFormData) => {
    try {
      setIsUpdating(true);
      setUpdateError(null);

      // Update the task via parent
      await onUpdate?.(task.id, {
        ...task,
        title: data.title,
        description: data.description,
        updatedAt: new Date(),
      });

      setIsEditing(false);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update task';
      setUpdateError({
        general: errorMessage,
      });
      console.error('Error updating task:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
      try {
        setIsDeleting(true);
        await onDelete?.(task.id);
      } catch (error) {
        console.error('Error deleting task:', error);
        // Optionally show error message to user
      } finally {
        setIsDeleting(false);
      }
    }
  };

  const handleToggleComments = () => {
    setShowCommentsSection(!showCommentsSection);
  };

  if (isEditing) {
    return (
      <div className={clsx(
        'border border-gray-200 rounded-lg bg-white shadow-sm',
        className
      )}>
        <TaskForm
          initialData={{
            title: task.title,
            description: task.description,
          }}
          onSubmit={handleUpdate}
          onCancel={handleCancelEdit}
          isSubmitting={isUpdating}
          submitButtonText="Update Task"
          showCancelButton={true}
          title="Edit Task"
          autoFocus={true}
          errors={updateError}
        />
      </div>
    );
  }

  return (
    <div className={clsx(
      'border border-gray-200 rounded-lg p-6 bg-white shadow-sm hover:shadow-md transition-shadow duration-200',
      className
    )}>
      {/* Task Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <H2 className="truncate">{task.title}</H2>
            {task.wasUpdated() && (
              <span className="text-xs text-gray-400 italic">Edited</span>
            )}
          </div>
          <ParagraphMedium className="text-gray-600 break-words">
            {task.description || <span className="text-gray-400 italic">No description</span>}
          </ParagraphMedium>
        </div>

        {/* Action buttons */}
        <div className="flex gap-2 ml-4 flex-shrink-0">
          {isOwnedByCurrentUser && (
            <>
              <Button
                type={ButtonType.BUTTON}
                kind={ButtonKind.TERTIARY}
                onClick={handleEdit}
                disabled={isDeleting || isUpdating}
                className="text-blue-500 hover:text-blue-700"
                title="Edit task"
              >
                Edit
              </Button>
              <Button
                type={ButtonType.BUTTON}
                kind={ButtonKind.TERTIARY}
                onClick={handleDelete}
                isLoading={isDeleting}
                disabled={isDeleting || isUpdating}
                className="text-red-500 hover:text-red-700"
                title="Delete task"
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Task Metadata */}
      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
        <div className="flex items-center gap-4">
          <span>Created {task.getFormattedDate()}</span>
          {task.wasUpdated() && (
            <span>Updated {task.getFormattedUpdatedDate()}</span>
          )}
          <span>{task.getReadingTime()}</span>
        </div>
        <div className="flex items-center gap-2">
          {isOwnedByCurrentUser && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
              Owner
            </span>
          )}
        </div>
      </div>

      {/* Comments Section */}
      {showComments && (
        <div className="border-t border-gray-100 pt-4">
          <Button
            type={ButtonType.BUTTON}
            kind={ButtonKind.SECONDARY}
            onClick={handleToggleComments}
            className="w-full text-left justify-start"
          >
            {showCommentsSection ? 'Hide Comments' : 'Show Comments'}
          </Button>

          {showCommentsSection && (
            <div className="mt-6">
              <CommentSection
                taskId={task.id}
                accountId={task.accountId}
                currentAccountId={currentAccountId}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TaskItem;