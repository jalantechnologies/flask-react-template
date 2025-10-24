import React from 'react';
import { Button } from 'frontend/components';

interface CommentFormProps {
  text: string;
  onTextChange: (value: string) => void;
  onSubmit: () => void;
  onCancel?: () => void;
  isEditing?: boolean;
}

export const CommentForm: React.FC<CommentFormProps> = ({
  text,
  onTextChange,
  onSubmit,
  onCancel,
  isEditing = false,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-6 p-6 bg-white dark:bg-boxdark rounded-lg shadow"
    >
      <div className="mb-4">
        <label className="mb-2.5 block font-medium text-black dark:text-white">
          Comment
        </label>
        <textarea
          value={text}
          onChange={(e) => onTextChange(e.target.value)}
          className="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary"
          rows={4}
          placeholder="Write your comment..."
          required
        />
      </div>

      <div className="flex gap-3">
        <Button type={'submit' as any}>
          {isEditing ? 'Update Comment' : 'Add Comment'}
        </Button>
        {isEditing && onCancel && (
          <Button type={'button' as any} onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};
