import React, { useEffect, useState, useCallback } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';

import { Button, Input, HorizontalStackLayout, VerticalStackLayout, ParagraphMedium } from 'frontend/components';
import { TaskService } from 'frontend/services';
import { Comment } from 'frontend/types/task';
import { ButtonType } from 'frontend/types/button';

interface CommentSectionProps {
    taskId: string;
}

const taskService = new TaskService();

const CommentSection: React.FC<CommentSectionProps> = ({ taskId }) => {
    const [comments, setComments] = useState<Comment[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const fetchComments = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await taskService.getComments(taskId);
            if (response.data) {
                setComments(response.data.items);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    }, [taskId]);

    useEffect(() => {
        fetchComments();
    }, [fetchComments]);

    const formik = useFormik({
        initialValues: { content: '' },
        validationSchema: Yup.object({
            content: Yup.string().required('Comment cannot be empty'),
        }),
        onSubmit: async (values, { resetForm }) => {
            try {
                await taskService.createComment(taskId, values.content);
                resetForm();
                fetchComments();
            } catch (err) {
                // Handle error (maybe show toast)
                console.error(err);
            }
        },
    });

    const handleDelete = async (commentId: string) => {
        if (window.confirm('Are you sure you want to delete this comment?')) {
            try {
                await taskService.deleteComment(commentId);
                fetchComments();
            } catch (err) {
                console.error(err);
            }
        }
    }

    return (
        <div className="mt-4 border-t pt-4">
            <h3 className="mb-4 text-lg font-semibold">Comments</h3>

            <div className="mb-4 max-h-60 overflow-y-auto">
                {isLoading && <p>Loading comments...</p>}
                {!isLoading && comments.length === 0 && <p className="text-gray-500">No comments yet.</p>}

                <VerticalStackLayout gap={3}>
                    {comments.map((comment) => (
                        <div key={comment.id} className="rounded-md bg-gray-50 p-3">
                            <ParagraphMedium>{comment.content}</ParagraphMedium>
                            <div className="mt-2 flex justify-between text-xs text-gray-400">
                                <span>{new Date(comment.createdAt).toLocaleString()}</span>
                                <button
                                    onClick={() => handleDelete(comment.id)}
                                    className="text-red-500 hover:text-red-700"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </VerticalStackLayout>
            </div>

            <form onSubmit={formik.handleSubmit}>
                <HorizontalStackLayout gap={2}>
                    <Input
                        name="content"
                        placeholder="Write a comment..."
                        value={formik.values.content}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        error={formik.touched.content ? formik.errors.content : undefined}
                    />
                    <Button type={ButtonType.SUBMIT} isLoading={formik.isSubmitting} disabled={!formik.isValid || !formik.dirty}>
                        Post
                    </Button>
                </HorizontalStackLayout>
            </form>
        </div>
    );
};

export default CommentSection;
