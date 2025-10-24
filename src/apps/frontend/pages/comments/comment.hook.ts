import { useState, useCallback } from 'react';
import {
  Comment,
  CreateCommentDto,
  UpdateCommentDto,
} from 'frontend/types/comments';

interface UseCommentsFormReturn {
  text: string;
  editingComment: Comment | null;
  setText: (value: string) => void;
  setEditingComment: (comment: Comment | null) => void;
  resetForm: () => void;
  populateForm: (comment: Comment) => void;
  getFormData: () => CreateCommentDto | UpdateCommentDto;
  isFormValid: () => boolean;
}

export const useCommentsForm = (): UseCommentsFormReturn => {
  const [text, setText] = useState('');
  const [editingComment, setEditingComment] = useState<Comment | null>(null);

  const resetForm = useCallback(() => {
    setText('');
    setEditingComment(null);
  }, []);

  const populateForm = useCallback((comment: Comment) => {
    setText(comment.text);
    setEditingComment(comment);
  }, []);

  const getFormData = useCallback((): CreateCommentDto | UpdateCommentDto => {
    return { text };
  }, [text]);

  const isFormValid = useCallback((): boolean => {
    return text.trim().length > 0;
  }, [text]);

  return {
    text,
    editingComment,
    setText,
    setEditingComment,
    resetForm,
    populateForm,
    getFormData,
    isFormValid,
  };
};
