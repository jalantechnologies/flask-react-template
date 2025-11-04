import React, { useState } from 'react';
import clsx from 'clsx';

import { Button } from 'frontend/components';
import { ParagraphMedium } from 'frontend/components/typography';
import { Comment } from 'frontend/types';
import { ButtonType, ButtonKind } from 'frontend/types/button';

interface CommentItemProps {
  comment: Comment;
  currentAccountId: string;
  onUpdate?: (commentId: string, content: string) => Promise<void>;
  onDelete?: (commentId: string) => Promise<void>;
  isUpdating?: boolean;
  isDeleting?: boolean;
  updatingCommentId?: string;
  deletingCommentId?: string;
}

const CommentItem: React.FC<CommentItemProps> = ({
  comment,
  currentAccountId,
  onUpdate,
  onDelete,
  isUpdating = false,
  isDeleting = false,
  updatingCommentId,
  deletingCommentId,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [error, setError] = useState<string | null>(null);

  const isOwnedByCurrentUser = comment.isOwnedBy(currentAccountId);
  const isCurrentlyUpdating = updatingCommentId === comment.id;
  const isCurrentlyDeleting = deletingCommentId === comment.id;
  const isDisabled = isEditing || isCurrentlyUpdating || isCurrentlyDeleting;

  const handleEdit = () => {
    setEditContent(comment.content);
    setError(null);
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setEditContent(comment.content);
    setError(null);
    setIsEditing(false);
  };

  const handleSaveEdit = async () => {
    const trimmedContent = editContent.trim();

    if (!trimmedContent) {
      setError('Comment cannot be empty');
      return;
    }

    if (trimmedContent.length > 2000) {
      setError('Comment cannot exceed 2000 characters');
      return;
    }

    if (trimmedContent === comment.content) {
      setIsEditing(false);
      return;
    }

    try {
      await onUpdate?.(comment.id, trimmedContent);
      setIsEditing(false);
      setError(null);
    } catch (err) {
      // Error is handled by parent
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this comment?')) {
      try {
        await onDelete?.(comment.id);
      } catch (err) {
        // Error is handled by parent
      }
    }
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className={clsx(
      'border-b border-gray-200 pb-4 last:border-b-0',
      isDisabled && 'opacity-60'
    )}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          {/* Author and timestamp */}
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-900">
              {comment.authorName}
            </span>
            <span className="text-sm text-gray-500">
              {formatDate(comment.createdAt)}
            </span>
            {comment.wasUpdated() && (
              <span className="text-xs text-gray-400 italic">
                (edited)
              </span>
            )}
          </div>

          {/* Comment content */}
          {isEditing ? (
            <div className="space-y-2">
              <textarea
                value={editContent}
                onChange={(e) => {
                  setEditContent(e.target.value);
                  if (error) setError(null);
                }}
                className="w-full min-h-[80px] rounded-lg border border-gray-300 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-y"
                autoFocus
                disabled={isCurrentlyUpdating}
                maxLength={2000}
              />
              {error && (
                <div className="text-sm text-red-500">
                  {error}
                </div>
              )}
              <div className="flex gap-2">
                <Button
                  type={ButtonType.BUTTON}
                  kind={ButtonKind.PRIMARY}
                  onClick={handleSaveEdit}
                  isLoading={isCurrentlyUpdating}
                  disabled={!editContent.trim() || isCurrentlyUpdating}
                >
                  Save
                </Button>
                <Button
                  type={ButtonType.BUTTON}
                  kind={ButtonKind.SECONDARY}
                  onClick={handleCancelEdit}
                  disabled={isCurrentlyUpdating}
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <ParagraphMedium className="text-gray-700 whitespace-pre-wrap">
              {comment.content}
            </ParagraphMedium>
          )}
        </div>

        {/* Action buttons */}
        {isOwnedByCurrentUser && !isEditing && (
          <div className="flex gap-1">
            <Button
              type={ButtonType.BUTTON}
              kind={ButtonKind.TERTIARY}
              onClick={handleEdit}
              disabled={isDisabled}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Edit
            </Button>
            <Button
              type={ButtonType.BUTTON}
              kind={ButtonKind.TERTIARY}
              onClick={handleDelete}
              isLoading={isCurrentlyDeleting}
              disabled={isDisabled}
              className="text-sm text-red-500 hover:text-red-700"
            >
              {isCurrentlyDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CommentItem;