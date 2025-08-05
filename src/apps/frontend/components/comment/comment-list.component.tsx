import React, { useEffect, useState } from 'react';
import { Comment, AccessToken } from 'frontend/types';
import { CommentService } from 'frontend/services';
import CommentItem from './comment-item.component';
import CommentForm from './comment-form.component';

interface CommentListProps {
  accessToken: AccessToken;
  taskId: string;
}

const CommentList: React.FC<CommentListProps> = ({ accessToken, taskId }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [editingCommentId, setEditingCommentId] = useState<string | null>(null);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  const commentService = new CommentService();

  useEffect(() => {
    const fetchComments = async () => {
      setLoading(true);
      try {
        const response = await commentService.getPaginatedComments(
          accessToken,
          taskId,
          page,
          10 // size
        );

        if (response.error) {
          setError(response.error.message);
        } else if (response.data) {
          setComments(response.data.items);
          setTotalPages(response.data.total_pages);
        }
      } catch (err) {
        setError('Failed to load comments');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchComments();
  }, [accessToken, taskId, page, refreshTrigger]);

  const handleCreateComment = async (content: string) => {
    try {
      await commentService.createComment(accessToken, taskId, content);
      // Refresh the comments list
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      setError('Failed to create comment');
      console.error(err);
    }
  };

  const handleUpdateComment = async (commentId: string, content: string) => {
    try {
      await commentService.updateComment(accessToken, taskId, commentId, content);
      setEditingCommentId(null);
      // Refresh the comments list
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      setError('Failed to update comment');
      console.error(err);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (window.confirm('Are you sure you want to delete this comment?')) {
      try {
        await commentService.deleteComment(accessToken, taskId, commentId);
        // Refresh the comments list
        setRefreshTrigger(prev => prev + 1);
      } catch (err) {
        setError('Failed to delete comment');
        console.error(err);
      }
    }
  };

  const handleEditClick = (commentId: string) => {
    setEditingCommentId(commentId);
  };

  const handleCancelEdit = () => {
    setEditingCommentId(null);
  };

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-4">Comments</h3>
      
      {/* New Comment Form */}
      <div className="mb-6">
        <CommentForm onSubmit={handleCreateComment} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 mb-4 text-red-700 bg-red-100 rounded">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="text-center p-4">Loading comments...</div>
      ) : (
        <>
          {/* Comments List */}
          {comments.length === 0 ? (
            <div className="text-center p-4 text-gray-500">No comments yet</div>
          ) : (
            <div>
              {comments.map(comment => (
                <div key={comment.id}>
                  {editingCommentId === comment.id ? (
                    <CommentForm
                      initialContent={comment.content}
                      onSubmit={(content) => handleUpdateComment(comment.id, content)}
                      onCancel={handleCancelEdit}
                      submitLabel="Update"
                    />
                  ) : (
                    <CommentItem
                      comment={comment}
                      isEditable={true}
                      onEdit={handleEditClick}
                      onDelete={handleDeleteComment}
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex justify-center mt-4 space-x-2">
              <button
                onClick={() => setPage(prev => Math.max(prev - 1, 1))}
                disabled={page === 1}
                className={`px-3 py-1 rounded ${page === 1 ? 'bg-gray-200 text-gray-500' : 'bg-blue-500 text-white hover:bg-blue-600'}`}
              >
                Previous
              </button>
              <span className="px-3 py-1">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(prev => Math.min(prev + 1, totalPages))}
                disabled={page === totalPages}
                className={`px-3 py-1 rounded ${page === totalPages ? 'bg-gray-200 text-gray-500' : 'bg-blue-500 text-white hover:bg-blue-600'}`}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default CommentList;