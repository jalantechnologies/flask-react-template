import React, { createContext, useContext, useReducer, useCallback, ReactNode } from 'react';
import { Comment } from 'frontend/types';

// State interface
interface CommentState {
  comments: Record<string, Comment[]>; // taskId -> comments array
  loading: Record<string, boolean>; // taskId -> loading state
  error: Record<string, string | null>; // taskId -> error
  pagination: Record<string, {
    totalCount: number;
    totalPages: number;
    currentPage: number;
    hasMore: boolean;
  }>;
}

// Action types
type CommentAction =
  | { type: 'SET_LOADING'; payload: { taskId: string; isLoading: boolean } }
  | { type: 'SET_ERROR'; payload: { taskId: string; error: string | null } }
  | { type: 'SET_COMMENTS'; payload: { taskId: string; comments: Comment[]; append?: boolean } }
  | { type: 'SET_PAGINATION'; payload: { taskId: string; pagination: any } }
  | { type: 'ADD_COMMENT'; payload: { taskId: string; comment: Comment } }
  | { type: 'UPDATE_COMMENT'; payload: { taskId: string; commentId: string; content: string; updatedAt: Date } }
  | { type: 'DELETE_COMMENT'; payload: { taskId: string; commentId: string } }
  | { type: 'CLEAR_TASK_COMMENTS'; payload: { taskId: string } };

// Initial state
const initialState: CommentState = {
  comments: {},
  loading: {},
  error: {},
  pagination: {},
};

// Reducer
const commentReducer = (state: CommentState, action: CommentAction): CommentState => {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: {
          ...state.loading,
          [action.payload.taskId]: action.payload.isLoading,
        },
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: {
          ...state.error,
          [action.payload.taskId]: action.payload.error,
        },
      };

    case 'SET_COMMENTS':
      const { taskId, comments, append = false } = action.payload;
      return {
        ...state,
        comments: {
          ...state.comments,
          [taskId]: append
            ? [...(state.comments[taskId] || []), ...comments]
            : comments,
        },
      };

    case 'SET_PAGINATION':
      return {
        ...state,
        pagination: {
          ...state.pagination,
          [action.payload.taskId]: action.payload.pagination,
        },
      };

    case 'ADD_COMMENT':
      return {
        ...state,
        comments: {
          ...state.comments,
          [action.payload.taskId]: [
            action.payload.comment,
            ...(state.comments[action.payload.taskId] || []),
          ],
        },
      };

    case 'UPDATE_COMMENT':
      const { taskId, commentId, content, updatedAt } = action.payload;
      return {
        ...state,
        comments: {
          ...state.comments,
          [taskId]: state.comments[taskId]?.map(comment =>
            comment.id === commentId
              ? { ...comment, content, updatedAt }
              : comment
          ) || [],
        },
      };

    case 'DELETE_COMMENT':
      const { taskId: deleteTaskId, commentId: deleteCommentId } = action.payload;
      return {
        ...state,
        comments: {
          ...state.comments,
          [deleteTaskId]: state.comments[deleteTaskId]?.filter(
            comment => comment.id !== deleteCommentId
          ) || [],
        },
      };

    case 'CLEAR_TASK_COMMENTS':
      const { taskId: clearTaskId } = action.payload;
      const newComments = { ...state.comments };
      const newLoading = { ...state.loading };
      const newError = { ...state.error };
      const newPagination = { ...state.pagination };

      delete newComments[clearTaskId];
      delete newLoading[clearTaskId];
      delete newError[clearTaskId];
      delete newPagination[clearTaskId];

      return {
        ...state,
        comments: newComments,
        loading: newLoading,
        error: newError,
        pagination: newPagination,
      };

    default:
      return state;
  }
};

// Context
interface CommentContextType {
  state: CommentState;
  actions: {
    setLoading: (taskId: string, isLoading: boolean) => void;
    setError: (taskId: string, error: string | null) => void;
    setComments: (taskId: string, comments: Comment[], pagination?: any, append?: boolean) => void;
    addComment: (taskId: string, comment: Comment) => void;
    updateComment: (taskId: string, commentId: string, content: string, updatedAt: Date) => void;
    deleteComment: (taskId: string, commentId: string) => void;
    clearTaskComments: (taskId: string) => void;
  };
}

const CommentContext = createContext<CommentContextType | null>(null);

// Provider
interface CommentProviderProps {
  children: ReactNode;
}

export const CommentProvider: React.FC<CommentProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(commentReducer, initialState);

  const setLoading = useCallback((taskId: string, isLoading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: { taskId, isLoading } });
  }, []);

  const setError = useCallback((taskId: string, error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: { taskId, error } });
  }, []);

  const setComments = useCallback((taskId: string, comments: Comment[], pagination?: any, append: boolean = false) => {
    dispatch({ type: 'SET_COMMENTS', payload: { taskId, comments, append } });
    if (pagination) {
      dispatch({ type: 'SET_PAGINATION', payload: { taskId, pagination } });
    }
  }, []);

  const addComment = useCallback((taskId: string, comment: Comment) => {
    dispatch({ type: 'ADD_COMMENT', payload: { taskId, comment } });
  }, []);

  const updateComment = useCallback((taskId: string, commentId: string, content: string, updatedAt: Date) => {
    dispatch({ type: 'UPDATE_COMMENT', payload: { taskId, commentId, content, updatedAt } });
  }, []);

  const deleteComment = useCallback((taskId: string, commentId: string) => {
    dispatch({ type: 'DELETE_COMMENT', payload: { taskId, commentId } });
  }, []);

  const clearTaskComments = useCallback((taskId: string) => {
    dispatch({ type: 'CLEAR_TASK_COMMENTS', payload: { taskId } });
  }, []);

  const actions = {
    setLoading,
    setError,
    setComments,
    addComment,
    updateComment,
    deleteComment,
    clearTaskComments,
  };

  return (
    <CommentContext.Provider value={{ state, actions }}>
      {children}
    </CommentContext.Provider>
  );
};

// Hook
export const useCommentContext = () => {
  const context = useContext(CommentContext);
  if (!context) {
    throw new Error('useCommentContext must be used within a CommentProvider');
  }
  return context;
};

export default CommentProvider;