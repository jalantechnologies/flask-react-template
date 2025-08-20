import React, { useState } from 'react';

import Button from 'frontend/components/button';
import HorizontalStackLayout from 'frontend/components/layouts/horizontal-stack-layout';
import VerticalStackLayout from 'frontend/components/layouts/vertical-stack-layout';
import CommentForm from 'frontend/components/task/comment-form';
import {
  ButtonKind,
  ButtonType,
  Comment,
  CommentFormData,
} from 'frontend/types';

interface CommentItemProps {
  comment: Comment;
  onUpdate: (commentId: string, data: CommentFormData) => Promise<void>;
  onDelete: (commentId: string) => Promise<void>;
  isLoading?: boolean;
}

const CommentItem: React.FC<CommentItemProps> = ({
  comment,
  onUpdate,
  onDelete,
  isLoading = false,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return (
        date.toLocaleDateString() +
        ' at ' +
        date.toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })
      );
    } catch {
      return dateString;
    }
  };

  const handleUpdate = async (data: CommentFormData) => {
    try {
      await onUpdate(comment.id, data);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update comment:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this comment?')) {
      setIsDeleting(true);
      try {
        await onDelete(comment.id);
      } catch (error) {
        console.error('Failed to delete comment:', error);
        setIsDeleting(false);
      }
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="bg-white rounded-lg border border-stroke p-4 shadow-sm">
        <CommentForm
          initialData={{ content: comment.content }}
          onSubmit={handleUpdate}
          onCancel={handleCancelEdit}
          submitLabel="Update Comment"
          isLoading={isLoading}
          placeholder="Edit your comment..."
        />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-stroke p-4 shadow-sm">
      <VerticalStackLayout gap={3}>
        <div className="text-sm text-gray-600 font-medium">
          {formatDate(comment.created_at)}
          {comment.updated_at !== comment.created_at && (
            <span className="text-gray-500"> (edited)</span>
          )}
        </div>

        <div className="text-gray-900 whitespace-pre-wrap">
          {comment.content}
        </div>

        <HorizontalStackLayout gap={2}>
          <Button
            type={ButtonType.BUTTON}
            kind={ButtonKind.TERTIARY}
            onClick={() => setIsEditing(true)}
            disabled={isLoading || isDeleting}
          >
            Edit
          </Button>
          <Button
            type={ButtonType.BUTTON}
            kind={ButtonKind.TERTIARY}
            onClick={handleDelete}
            disabled={isLoading || isDeleting}
            isLoading={isDeleting}
          >
            Delete
          </Button>
        </HorizontalStackLayout>
      </VerticalStackLayout>
    </div>
  );
};

export default CommentItem;
