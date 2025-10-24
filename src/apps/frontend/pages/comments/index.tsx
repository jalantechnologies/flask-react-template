import React, { useEffect } from 'react';
import toast from 'react-hot-toast';
import { useParams } from 'react-router-dom';
import { useCommentContext } from 'frontend/contexts/comment.provider';
import { CommentForm } from './comment-form.component';
import { CommentItem } from './comment-item.component';
import { useCommentsForm } from './comment.hook';
import { Comment } from 'frontend/types/comments';
import { useAccountContext } from 'frontend/contexts';

const Comments: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const { accountDetails } = useAccountContext();
  const {
    comments,
    isLoading,
    setAccountAndTaskId,
    fetchComments,
    createComment,
    updateComment,
    deleteComment,
  } = useCommentContext();

  const {
    text,
    editingComment,
    setText,
    resetForm,
    populateForm,
    getFormData,
    isFormValid,
  } = useCommentsForm();

  useEffect(() => {
    if (accountDetails?.id && taskId) {
      setAccountAndTaskId(accountDetails.id, taskId);
      fetchComments(accountDetails.id, taskId).catch((err: Error) => {
        toast.error(err.message || 'Failed to load comments');
      });
    }
  }, [accountDetails?.id, taskId, setAccountAndTaskId, fetchComments]);

  const handleSubmit = async () => {
    if (!isFormValid()) {
      toast.error('Please enter a comment');
      return;
    }

    try {
      if (editingComment) {
        await updateComment(editingComment.id, getFormData());
        toast.success('Comment updated successfully');
      } else {
        await createComment(getFormData());
        toast.success('Comment added successfully');
      }
      resetForm();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      const error = err as Error;
      toast.error(error.message || 'Failed to save comment');
    }
  };

  const handleEdit = (comment: Comment) => {
    populateForm(comment);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteComment(id);
      toast.success('Comment deleted successfully');
    } catch (err) {
      const error = err as Error;
      toast.error(error.message || 'Failed to delete comment');
    }
  };

  if (isLoading && comments.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-black dark:text-white">
          Loading comments...
        </div>
      </div>
    );
  }

  if (!taskId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-black dark:text-white">
          Task ID is required
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-screen-xl p-4 md:p-6 2xl:p-10">
      <div className="mb-6">
        <h1 className="text-title-md2 font-semibold text-black dark:text-white">
          Comments
        </h1>
      </div>

      <CommentForm
        text={text}
        onTextChange={setText}
        onSubmit={handleSubmit}
        onCancel={editingComment ? resetForm : undefined}
        isEditing={!!editingComment}
      />

      <div className="mt-8">
        <h2 className="text-title-md font-semibold text-black dark:text-white mb-4">
          All Comments ({comments.length})
        </h2>

        {comments.length === 0 ? (
          <div className="rounded-sm border border-stroke bg-white p-10 shadow-default dark:border-strokedark dark:bg-boxdark">
            <p className="text-center text-bodydark">
              No comments yet. Be the first to comment!
            </p>
          </div>
        ) : (
          comments.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default Comments;
