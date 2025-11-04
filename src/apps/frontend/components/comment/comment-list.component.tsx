import React from 'react';
import clsx from 'clsx';

import { Button } from 'frontend/components';
import { H2, ParagraphMedium } from 'frontend/components/typography';
import { Comment, CommentListResponse } from 'frontend/types';
import { ButtonType, ButtonKind } from 'frontend/types/button';
import CommentItem from './comment-item.component';

interface CommentListProps {
  comments: Comment[];
  currentAccountId: string;
  totalCount: number;
  totalPages: number;
  currentPage: number;
  isLoading?: boolean;
  error?: string | null;
  onLoadMore?: () => void;
  onUpdateComment?: (commentId: string, content: string) => Promise<void>;
  onDeleteComment?: (commentId: string) => Promise<void>;
  isUpdating?: boolean;
  isDeleting?: boolean;
  updatingCommentId?: string;
  deletingCommentId?: string;
  hasMore?: boolean;
}

const CommentList: React.FC<CommentListProps> = ({
  comments,
  currentAccountId,
  totalCount,
  totalPages,
  currentPage,
  isLoading = false,
  error = null,
  onLoadMore,
  onUpdateComment,
  onDeleteComment,
  isUpdating = false,
  isDeleting = false,
  updatingCommentId,
  deletingCommentId,
  hasMore = false,
}) => {
  if (isLoading && comments.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">Loading comments...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-red-500">Error loading comments: {error}</div>
      </div>
    );
  }

  if (comments.length === 0 && !isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">No comments yet. Be the first to comment!</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <H2>Comments ({totalCount})</H2>
        {totalCount > comments.length && (
          <span className="text-sm text-gray-500">
            Showing {comments.length} of {totalCount}
          </span>
        )}
      </div>

      {/* Comments */}
      <div className={clsx(
        'space-y-4',
        // Add loading state to the list when fetching more
        isLoading && 'opacity-60'
      )}>
        {comments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            currentAccountId={currentAccountId}
            onUpdate={onUpdateComment}
            onDelete={onDeleteComment}
            isUpdating={isUpdating}
            isDeleting={isDeleting}
            updatingCommentId={updatingCommentId}
            deletingCommentId={deletingCommentId}
          />
        ))}
      </div>

      {/* Load more button */}
      {hasMore && onLoadMore && (
        <div className="flex justify-center pt-4">
          <Button
            type={ButtonType.BUTTON}
            kind={ButtonKind.SECONDARY}
            onClick={onLoadMore}
            isLoading={isLoading}
            disabled={isLoading}
            className="w-full max-w-xs"
          >
            {isLoading ? 'Loading...' : 'Load More Comments'}
          </Button>
        </div>
      )}

      {/* Loading indicator for initial load */}
      {isLoading && comments.length === 0 && (
        <div className="flex items-center justify-center py-8">
          <div className="text-gray-500">Loading comments...</div>
        </div>
      )}
    </div>
  );
};

export default CommentList;