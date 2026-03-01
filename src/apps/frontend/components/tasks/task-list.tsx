import React, { useCallback, useEffect, useState } from 'react';
import { Button, H2, VerticalStackLayout, ParagraphMedium } from 'frontend/components';
import { TaskService } from 'frontend/services';
import { AsyncError } from 'frontend/types/async-operation';
import { Task } from 'frontend/types/task';
import TaskItem from './task-item';
import TaskForm from './task-form';

const taskService = new TaskService();

const TaskList: React.FC = () => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<AsyncError | null>(null);
    const [isCreating, setIsCreating] = useState(false);

    const fetchTasks = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await taskService.getTasks(1, 100); // Fetch up to 100 tasks for now
            if (response.data) {
                setTasks(response.data.items);
            }
        } catch (err) {
            setError(err as AsyncError);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchTasks();
    }, [fetchTasks]);

    const handleCreate = async (values: { title: string; description: string }) => {
        try {
            await taskService.createTask(values.title, values.description);
            setIsCreating(false);
            fetchTasks();
        } catch (err) {
            console.error(err);
            // specific error handling could go here
        }
    };

    const handleUpdate = async (taskId: string, title: string, description: string) => {
        try {
            await taskService.updateTask(taskId, title, description);
            fetchTasks();
        } catch (err) {
            console.error(err);
        }
    };

    const handleDelete = async (taskId: string) => {
        try {
            await taskService.deleteTask(taskId);
            fetchTasks();
        } catch (err) {
            console.error(err);
        }
    };

    if (error) {
        return <ParagraphMedium className="text-red-500">Error loading tasks: {error.message}</ParagraphMedium>;
    }

    return (
        <div className="mx-auto max-w-4xl p-6">
            <div className="mb-6 flex items-center justify-between">
                <H2>Tasks</H2>
                {!isCreating && (
                    <Button onClick={() => setIsCreating(true)}>
                        Create Task
                    </Button>
                )}
            </div>

            {isCreating && (
                <div className="mb-8 rounded-lg border bg-gray-50 p-6">
                    <H2 className="mb-4">New Task</H2>
                    <TaskForm
                        onSubmit={handleCreate}
                        onCancel={() => setIsCreating(false)}
                        submitLabel="Create Task"
                    />
                </div>
            )}

            {isLoading && <ParagraphMedium>Loading tasks...</ParagraphMedium>}

            {!isLoading && tasks.length === 0 && !isCreating && (
                <div className="text-center py-10">
                    <ParagraphMedium className="text-gray-500">No tasks found. Create one to get started!</ParagraphMedium>
                </div>
            )}

            <VerticalStackLayout gap={6}>
                {tasks.map((task) => (
                    <TaskItem
                        key={task.id}
                        task={task}
                        onUpdate={handleUpdate}
                        onDelete={handleDelete}
                    />
                ))}
            </VerticalStackLayout>
        </div>
    );
};

export default TaskList;
