import React from 'react';

import Button from 'frontend/components/button';
import HorizontalStackLayout from 'frontend/components/layouts/horizontal-stack-layout';
import VerticalStackLayout from 'frontend/components/layouts/vertical-stack-layout';
import ParagraphMedium from 'frontend/components/typography/paragraph-medium';
import { ButtonKind } from 'frontend/types/button';
import { Task } from 'frontend/types/task';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
  isDeleting?: boolean;
}

const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onEdit,
  onDelete,
  isDeleting = false,
}) => {
  const formatDate = (dateString: string) =>
    new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

  return (
    <div className="rounded-lg border border-stroke bg-white p-6 shadow-sm">
      <VerticalStackLayout gap={4}>
        <div>
          <div className="mb-2 text-lg font-semibold text-gray-900">
            {task.title}
          </div>
          <ParagraphMedium>{task.description}</ParagraphMedium>
        </div>

        <div className="text-sm text-gray-500">
          <p>Created: {formatDate(task.created_at)}</p>
          <p>Updated: {formatDate(task.updated_at)}</p>
        </div>

        <HorizontalStackLayout gap={2}>
          <Button kind={ButtonKind.SECONDARY} onClick={() => onEdit(task)}>
            Edit
          </Button>
          <Button
            kind={ButtonKind.TERTIARY}
            onClick={() => onDelete(task.id)}
            disabled={isDeleting}
            isLoading={isDeleting}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </HorizontalStackLayout>
      </VerticalStackLayout>
    </div>
  );
};

export default TaskCard;
