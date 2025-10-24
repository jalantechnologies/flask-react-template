import React, { createContext, useContext, useState, useCallback } from 'react';
import commentService from 'frontend/services/comment.service';
import {
  Comment,
  CreateCommentDto,
  UpdateCommentDto,
} from 'frontend/types/comments';

interface CommentContextValue {
  comments: Comment[];
  isLoading: boolean;
  error: string | null;
  accountId: string | null;
  taskId: string | null;
  setAccountAndTaskId: (accountId: string, taskId: string) => void;
  fetchComments: (accountId: string, taskId: string) => Promise<void>;
  createComment: (dto: CreateCommentDto) => Promise<Comment>;
  updateComment: (commentId: string, dto: UpdateCommentDto) => Promise<Comment>;
  deleteComment: (commentId: string) => Promise<void>;
}

const CommentContext = createContext<CommentContextValue | undefined>(
  undefined,
);

export const CommentProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [accountId, setAccountId] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  const setAccountAndTaskId = useCallback((accId: string, tId: string) => {
    setAccountId(accId);
    setTaskId(tId);
  }, []);

  const fetchComments = useCallback(async (accId: string, tId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await commentService.getAllComments(accId, tId);
      setComments(data);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.message ||
        err.message ||
        'Failed to fetch comments';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createComment = useCallback(
    async (dto: CreateCommentDto): Promise<Comment> => {
      if (!accountId || !taskId) {
        throw new Error('Account ID and Task ID are required');
      }

      try {
        const data = await commentService.createComment(accountId, taskId, dto);
        setComments((prev) => [data, ...prev]);
        return data;
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.message ||
          err.message ||
          'Failed to create comment';
        throw new Error(errorMessage);
      }
    },
    [accountId, taskId],
  );

  const updateComment = useCallback(
    async (commentId: string, dto: UpdateCommentDto): Promise<Comment> => {
      if (!accountId || !taskId) {
        throw new Error('Account ID and Task ID are required');
      }

      try {
        const data = await commentService.updateComment(
          accountId,
          taskId,
          commentId,
          dto,
        );
        setComments((prev) => prev.map((c) => (c.id === commentId ? data : c)));
        return data;
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.message ||
          err.message ||
          'Failed to update comment';
        throw new Error(errorMessage);
      }
    },
    [accountId, taskId],
  );

  const deleteComment = useCallback(
    async (commentId: string): Promise<void> => {
      if (!accountId || !taskId) {
        throw new Error('Account ID and Task ID are required');
      }

      try {
        await commentService.deleteComment(accountId, taskId, commentId);
        setComments((prev) => prev.filter((c) => c.id !== commentId));
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.message ||
          err.message ||
          'Failed to delete comment';
        throw new Error(errorMessage);
      }
    },
    [accountId, taskId],
  );

  const value: CommentContextValue = {
    comments,
    isLoading,
    error,
    accountId,
    taskId,
    setAccountAndTaskId,
    fetchComments,
    createComment,
    updateComment,
    deleteComment,
  };

  return (
    <CommentContext.Provider value={value}>{children}</CommentContext.Provider>
  );
};

export const useCommentContext = (): CommentContextValue => {
  const context = useContext(CommentContext);
  if (!context) {
    throw new Error('useCommentContext must be used within CommentProvider');
  }
  return context;
};
