import React, { useState } from 'react';

interface CommentFormProps {
  initialContent?: string;
  onSubmit: (content: string) => void;
  onCancel?: () => void;
  submitLabel?: string;
}

const CommentForm: React.FC<CommentFormProps> = ({
  initialContent = '',
  onSubmit,
  onCancel,
  submitLabel = 'Submit',
}) => {
  const [content, setContent] = useState<string>(initialContent);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) {
      return;
    }
    
    setIsSubmitting(true);
    try {
      await onSubmit(content);
      // Clear the form if it's a new comment (not editing)
      if (!initialContent) {
        setContent('');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <div className="mb-3">
        <textarea
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
          placeholder="Write a comment..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          disabled={isSubmitting}
        />
      </div>
      <div className="flex justify-end space-x-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300 focus:outline-none"
            disabled={isSubmitting}
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          className="px-4 py-2 text-white bg-blue-500 rounded hover:bg-blue-600 focus:outline-none disabled:opacity-50"
          disabled={isSubmitting || !content.trim()}
        >
          {isSubmitting ? 'Submitting...' : submitLabel}
        </button>
      </div>
    </form>
  );
};

export default CommentForm;