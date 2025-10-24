import React from 'react';
import { Button } from 'frontend/components';
import { Comment } from 'frontend/types/comments';

interface CommentItemProps {
  comment: Comment;
  onEdit: (comment: Comment) => void;
  onDelete: (id: string) => void;
}

export const CommentItem: React.FC<CommentItemProps> = ({
  comment,
  onEdit,
  onDelete,
}) => {
  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this comment?')) {
      onDelete(comment.id);
    }
  };

  return (
    <div className="rounded-sm border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-boxdark mb-4">
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-sm text-bodydark">
            {new Date(comment.created_at).toLocaleString()}
            {comment.updated_at && (
              <span className="ml-2 text-meta-3">(edited)</span>
            )}
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => onEdit(comment)}>Edit</Button>
          <Button onClick={handleDelete}>Delete</Button>
        </div>
      </div>
      <p className="text-body">{comment.text}</p>
    </div>
  );
};
