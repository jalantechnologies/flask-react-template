import React, { useState, useEffect } from 'react';

import Button from 'frontend/components/button';
import VerticalStackLayout from 'frontend/components/layouts/vertical-stack-layout';
import CommentForm from 'frontend/components/task/comment-form';
import CommentItem from 'frontend/components/task/comment-item';
import CommentService from 'frontend/services/comment.service';
import {
  ButtonKind,
  ButtonType,
  Comment,
  CommentFormData,
} from 'frontend/types';

interface CommentListProps {
  taskId: string;
}

const CommentList: React.FC<CommentListProps> = ({ taskId }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string>('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const commentService = new CommentService();

  const fetchComments = async (
    pageNum: number = 1,
    append: boolean = false,
  ) => {
    try {
      setIsLoading(true);
      const response = await commentService.getComments(taskId, pageNum, 10);

      if (response && response.data) {
        const newComments = response.data.items;
        setComments((prev) =>
          append ? [...prev, ...newComments] : newComments,
        );
        setTotalCount(response.data.total_count);
        setHasMore(pageNum < response.data.total_pages);
        setPage(pageNum);
      } else {
        setError('Failed to load comments');
      }
    } catch (err) {
      setError('Failed to load comments');
      console.error('Error fetching comments:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchComments();
  }, [taskId]);

  const handleAddComment = async (data: CommentFormData) => {
    setIsSubmitting(true);
    setError('');

    try {
      const response = await commentService.createComment(taskId, {
        content: data.content,
      });

      if (response && response.data) {
        setComments((prev) => [response.data!, ...prev]);
        setTotalCount((prev) => prev + 1);
      } else {
        setError('Failed to add comment');
      }
    } catch (err) {
      setError('Failed to add comment');
      console.error('Error creating comment:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateComment = async (
    commentId: string,
    data: CommentFormData,
  ) => {
    try {
      const response = await commentService.updateComment(taskId, commentId, {
        content: data.content,
      });

      if (response && response.data) {
        setComments((prev) =>
          prev.map((comment) =>
            comment.id === commentId ? response.data! : comment,
          ),
        );
      } else {
        throw new Error('Update failed');
      }
    } catch (err) {
      console.error('Error updating comment:', err);
      throw err;
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    try {
      await commentService.deleteComment(taskId, commentId);
      setComments((prev) => prev.filter((comment) => comment.id !== commentId));
      setTotalCount((prev) => prev - 1);
    } catch (err) {
      console.error('Error deleting comment:', err);
      throw err;
    }
  };

  const handleLoadMore = () => {
    fetchComments(page + 1, true);
  };

  if (isLoading && comments.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <div className="text-gray-500">Loading comments...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Comments ({totalCount})
        </h3>

        <CommentForm
          onSubmit={handleAddComment}
          isLoading={isSubmitting}
          placeholder="Add a comment..."
        />

        {error && (
          <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}
      </div>

      {comments.length > 0 ? (
        <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 bg-gray-50">
          <VerticalStackLayout gap={4}>
            {comments.map((comment) => (
              <CommentItem
                key={comment.id}
                comment={comment}
                onUpdate={handleUpdateComment}
                onDelete={handleDeleteComment}
                isLoading={isSubmitting}
              />
            ))}

            {hasMore && (
              <div className="text-center pt-4 border-t border-gray-300 mt-4">
                <Button
                  type={ButtonType.BUTTON}
                  kind={ButtonKind.TERTIARY}
                  onClick={handleLoadMore}
                  isLoading={isLoading}
                  disabled={isLoading}
                >
                  Load More Comments
                </Button>
              </div>
            )}
          </VerticalStackLayout>
        </div>
      ) : (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <div className="text-gray-500">
            No comments yet. Be the first to comment!
          </div>
        </div>
      )}
    </div>
  );
};

export default CommentList;
