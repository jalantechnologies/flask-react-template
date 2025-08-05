import React from 'react';
import { Comment } from 'frontend/types';

interface CommentItemProps {
  comment: Comment;
  onEdit?: (commentId: string) => void;
  onDelete?: (commentId: string) => void;
  isEditable?: boolean;
}

const CommentItem: React.FC<CommentItemProps> = ({
  comment,
  onEdit,
  onDelete,
  isEditable = false,
}) => {
  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="p-4 mb-3 bg-white rounded shadow">
      <div className="flex justify-between items-start mb-2">
        <div className="text-sm text-gray-500">
          {formatDate(comment.createdAt)}
          {comment.updatedAt > comment.createdAt && (
            <span className="ml-2 italic">(edited)</span>
          )}
        </div>
        {isEditable && (
          <div className="flex space-x-2">
            <button
              onClick={() => onEdit && onEdit(comment.id)}
              className="text-blue-500 hover:text-blue-700 text-sm"
            >
              Edit
            </button>
            <button
              onClick={() => onDelete && onDelete(comment.id)}
              className="text-red-500 hover:text-red-700 text-sm"
            >
              Delete
            </button>
          </div>
        )}
      </div>
      <div className="text-gray-800 whitespace-pre-wrap">{comment.content}</div>
    </div>
  );
};

export default CommentItem;