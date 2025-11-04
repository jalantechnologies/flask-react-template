import React, { useState, useEffect } from 'react';
import clsx from 'clsx';

import { Button } from 'frontend/components';
import FormControl from 'frontend/components/form-control';
import { ParagraphMedium } from 'frontend/components/typography';

interface CommentFormProps {
  onSubmit: (content: string) => Promise<void>;
  onCancel?: () => void;
  initialValue?: string;
  isSubmitting?: boolean;
  placeholder?: string;
  buttonText?: string;
  showCancelButton?: boolean;
  maxLength?: number;
  autoFocus?: boolean;
}

const CommentForm: React.FC<CommentFormProps> = ({
  onSubmit,
  onCancel,
  initialValue = '',
  isSubmitting = false,
  placeholder = 'Write a comment...',
  buttonText = 'Post Comment',
  showCancelButton = false,
  maxLength = 2000,
  autoFocus = false,
}) => {
  const [content, setContent] = useState(initialValue);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setContent(initialValue);
    setError(null);
  }, [initialValue]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous errors
    setError(null);

    // Validation
    const trimmedContent = content.trim();
    if (!trimmedContent) {
      setError('Comment cannot be empty');
      return;
    }

    if (trimmedContent.length > maxLength) {
      setError(`Comment cannot exceed ${maxLength} characters`);
      return;
    }

    try {
      await onSubmit(trimmedContent);
      setContent(''); // Clear form on successful submission
    } catch (err) {
      // Error is handled by the parent component
    }
  };

  const handleCancel = () => {
    setContent('');
    setError(null);
    onCancel?.();
  };

  const characterCount = content.length;
  const isOverLimit = characterCount > maxLength;
  const remainingCharacters = maxLength - characterCount;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <FormControl label="Comment" error={error}>
        <textarea
          value={content}
          onChange={(e) => {
            setContent(e.target.value);
            if (error) setError(null);
          }}
          placeholder={placeholder}
          maxLength={maxLength}
          autoFocus={autoFocus}
          disabled={isSubmitting}
          className={clsx(
            'w-full min-h-[100px] rounded-lg border border-gray-300 p-3 text-sm',
            'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'disabled:bg-gray-100 disabled:cursor-not-allowed',
            'resize-y',
            error && 'border-red-500 focus:ring-red-500',
            isOverLimit && 'border-red-500 focus:ring-red-500'
          )}
          rows={4}
        />
      </FormControl>

      <div className="flex items-center justify-between">
        <ParagraphMedium
          className={clsx(
            'text-xs',
            isOverLimit ? 'text-red-500' : 'text-gray-500'
          )}
        >
          {remainingCharacters} characters remaining
        </ParagraphMedium>

        <div className="flex gap-2">
          {showCancelButton && (
            <Button
              type={ButtonType.BUTTON}
              kind={ButtonKind.SECONDARY}
              onClick={handleCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          )}

          <Button
            type={ButtonType.SUBMIT}
            isLoading={isSubmitting}
            disabled={!content.trim() || isOverLimit || isSubmitting}
          >
            {buttonText}
          </Button>
        </div>
      </div>
    </form>
  );
};

export default CommentForm;