import React, { useState } from 'react';

import Button from 'frontend/components/button';
import VerticalStackLayout from 'frontend/components/layouts/vertical-stack-layout';
import { ButtonKind, ButtonType, CommentFormData } from 'frontend/types';

interface CommentFormProps {
  initialData?: Partial<CommentFormData>;
  onSubmit: (data: CommentFormData) => void;
  onCancel?: () => void;
  submitLabel?: string;
  isLoading?: boolean;
  placeholder?: string;
}

const CommentForm: React.FC<CommentFormProps> = ({
  initialData = {},
  onSubmit,
  onCancel,
  submitLabel = 'Add Comment',
  isLoading = false,
  placeholder = 'Write your comment...',
}) => {
  const [formData, setFormData] = useState<CommentFormData>({
    content: initialData.content || '',
  });

  const [error, setError] = useState<string>('');

  const validateForm = (): boolean => {
    if (!formData.content.trim()) {
      setError('Comment cannot be empty');
      return false;
    }
    setError('');
    return true;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
      if (!initialData.content) {
        // Reset form only for new comments, not edits
        setFormData({ content: '' });
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFormData({ content: e.target.value });
    if (error) {
      setError('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <VerticalStackLayout gap={3}>
        <div>
          <div className="w-full rounded-lg border border-stroke bg-white p-3 outline-none focus-within:border-primary">
            <textarea
              value={formData.content}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={isLoading}
              rows={3}
              className="w-full appearance-none outline-none resize-none text-sm"
            />
          </div>
          {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
          <p className="mt-1 text-xs text-gray-500">
            Press Ctrl+Enter to submit
          </p>
        </div>

        <div className="flex gap-2 justify-end">
          <Button
            type={ButtonType.SUBMIT}
            kind={ButtonKind.PRIMARY}
            isLoading={isLoading}
            disabled={isLoading || !formData.content.trim()}
          >
            {submitLabel}
          </Button>
          {onCancel && (
            <Button
              type={ButtonType.BUTTON}
              kind={ButtonKind.TERTIARY}
              onClick={onCancel}
              disabled={isLoading}
            >
              Cancel
            </Button>
          )}
        </div>
      </VerticalStackLayout>
    </form>
  );
};

export default CommentForm;
