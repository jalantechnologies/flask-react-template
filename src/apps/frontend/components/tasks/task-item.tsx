import React, { useState } from 'react';
import { Button, HorizontalStackLayout, VerticalStackLayout, ParagraphMedium, H2 } from 'frontend/components';
import { ButtonKind } from 'frontend/types/button';
import { Task } from 'frontend/types/task';
import CommentSection from './comment-section';
import TaskForm from './task-form';

interface TaskItemProps {
    task: Task;
    onUpdate: (taskId: string, title: string, description: string) => Promise<void>;
    onDelete: (taskId: string) => Promise<void>;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onUpdate, onDelete }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [showComments, setShowComments] = useState(false);

    const handleUpdate = async (values: { title: string; description: string }) => {
        await onUpdate(task.id, values.title, values.description);
        setIsEditing(false);
    };

    if (isEditing) {
        return (
            <div className="rounded-lg border bg-white p-6 shadow-sm">
                <TaskForm
                    initialValues={{ title: task.title, description: task.description }}
                    onSubmit={handleUpdate}
                    onCancel={() => setIsEditing(false)}
                    submitLabel="Update Task"
                />
            </div>
        );
    }

    return (
        <div className="rounded-lg border bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
            <VerticalStackLayout gap={4}>
                <div className="flex justify-between items-start">
                    <div className="flex-1">
                        <H2>{task.title}</H2>
                        <ParagraphMedium className="mt-2 text-gray-600">
                            {task.description}
                        </ParagraphMedium>
                        <div className="mt-4 text-xs text-gray-400">
                            Created: {new Date(task.createdAt).toLocaleDateString()}
                        </div>
                    </div>

                    <HorizontalStackLayout gap={2}>
                        <Button kind={ButtonKind.SECONDARY} onClick={() => setIsEditing(true)}>
                            Edit
                        </Button>
                        <Button
                            kind={ButtonKind.DANGER}
                            onClick={() => {
                                if (window.confirm('Are you sure you want to delete this task?')) {
                                    onDelete(task.id);
                                }
                            }}
                        >
                            Delete
                        </Button>
                    </HorizontalStackLayout>
                </div>

                <div className="border-t pt-2">
                    <Button kind={ButtonKind.TERTIARY} onClick={() => setShowComments(!showComments)}>
                        {showComments ? 'Hide Comments' : 'Show Comments'}
                    </Button>

                    {showComments && <CommentSection taskId={task.id} />}
                </div>
            </VerticalStackLayout>
        </div>
    );
};

export default TaskItem;
