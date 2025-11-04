import React, { useState, useCallback, useEffect } from 'react';
import clsx from 'clsx';

import { VerticalStackLayout } from 'frontend/components';
import CommentForm from './comment-form.component';
import CommentList from './comment-list.component';
import { Comment, CommentListResponse, PaginationParams } from 'frontend/types';
import CommentService from 'frontend/services/comment.service';

interface CommentSectionProps {
  taskId: string;
  accountId: string;
  currentAccountId: string;
  className?: string;
}

const CommentSection: React.FC<CommentSectionProps> = ({
  taskId,
  accountId,
  currentAccountId,
  className,
}) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form submission state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Update/delete state
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [updatingCommentId, setUpdatingCommentId] = useState<string | null>(null);
  const [deletingCommentId, setDeletingCommentId] = useState<string | null>(null);

  const commentService = new CommentService();

  const pageSize = 10;
  const hasMore = currentPage < totalPages;
  const paginationParams = new PaginationParams(currentPage, pageSize);

  // Load comments
  const loadComments = useCallback(async (page: number = 1, append: boolean = false) => {
    try {
      setIsLoading(true);
      setError(null);

      const params = new PaginationParams(page, pageSize);
      const response = await commentService.getComments(accountId, taskId, params);

      if (response.data) {
        const newComments = response.data.items;

        if (append) {
          setComments(prev => [...prev, ...newComments]);
        } else {
          setComments(newComments);
        }

        setTotalCount(response.data.totalCount);
        setTotalPages(response.data.totalPages);
        setCurrentPage(page);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load comments';
      setError(errorMessage);
      console.error('Error loading comments:', err);
    } finally {
      setIsLoading(false);
    }
  }, [accountId, taskId, commentService]);

  // Initial load
  useEffect(() => {
    loadComments(1, false);
  }, [loadComments]);

  // Handle comment submission
  const handleCommentSubmit = useCallback(async (content: string) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);

      const response = await commentService.createComment(accountId, taskId, content);

      if (response.data) {
        // Add new comment to the beginning of the list
        setComments(prev => [response.data!, ...prev]);
        setTotalCount(prev => prev + 1);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to post comment';
      setSubmitError(errorMessage);
      console.error('Error submitting comment:', err);
      throw err; // Re-throw to let the form handle it
    } finally {
      setIsSubmitting(false);
    }
  }, [accountId, taskId, commentService]);

  // Handle comment update
  const handleCommentUpdate = useCallback(async (commentId: string, content: string) => {
    try {
      setIsUpdating(true);
      setUpdatingCommentId(commentId);

      const response = await commentService.updateComment(accountId, taskId, commentId, content);

      if (response.data) {
        setComments(prev => prev.map(comment =>
          comment.id === commentId ? response.data! : comment
        ));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update comment';
      console.error('Error updating comment:', err);
      throw err; // Re-throw to let the item component handle it
    } finally {
      setIsUpdating(false);
      setUpdatingCommentId(null);
    }
  }, [accountId, taskId, commentService]);

  // Handle comment deletion
  const handleCommentDelete = useCallback(async (commentId: string) => {
    try {
      setIsDeleting(true);
      setDeletingCommentId(commentId);

      await commentService.deleteComment(accountId, taskId, commentId);

      // Remove comment from the list
      setComments(prev => prev.filter(comment => comment.id !== commentId));
      setTotalCount(prev => prev - 1);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete comment';
      console.error('Error deleting comment:', err);
      throw err; // Re-throw to let the item component handle it
    } finally {
      setIsDeleting(false);
      setDeletingCommentId(null);
    }
  }, [accountId, taskId, commentService]);

  // Handle load more
  const handleLoadMore = useCallback(() => {
    if (hasMore && !isLoading) {
      loadComments(currentPage + 1, true);
    }
  }, [hasMore, isLoading, currentPage, loadComments]);

  return (
    <div className={clsx('w-full max-w-4xl mx-auto', className)}>
      <VerticalStackLayout gap={8}>
        {/* Comment Form */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-medium mb-4">Add a Comment</h3>
          {submitError && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
              {submitError}
            </div>
          )}
          <CommentForm
            onSubmit={handleCommentSubmit}
            isSubmitting={isSubmitting}
            buttonText="Post Comment"
            placeholder="Share your thoughts..."
          />
        </div>

        {/* Comments List */}
        <div>
          <CommentList
            comments={comments}
            currentAccountId={currentAccountId}
            totalCount={totalCount}
            totalPages={totalPages}
            currentPage={currentPage}
            isLoading={isLoading}
            error={error}
            onLoadMore={handleLoadMore}
            onUpdateComment={handleCommentUpdate}
            onDeleteComment={handleCommentDelete}
            isUpdating={isUpdating}
            isDeleting={isDeleting}
            updatingCommentId={updatingCommentId}
            deletingCommentId={deletingCommentId}
            hasMore={hasMore}
          />
        </div>
      </VerticalStackLayout>
    </div>
  );
};

export default CommentSection;