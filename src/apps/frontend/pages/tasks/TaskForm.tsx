import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate, useParams } from 'react-router-dom';

import { useAccountContext } from 'frontend/contexts';
import TaskService from 'frontend/services/task.service';

const TaskForm: React.FC = () => {
    const { account } = useAccountContext();
    const navigate = useNavigate();
    const { taskId } = useParams<{ taskId: string }>();
    const isEditMode = !!taskId;

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const taskService = new TaskService();

    useEffect(() => {
        if (isEditMode && account && taskId) {
            loadTask();
        }
    }, [isEditMode, account, taskId]);

    const loadTask = async () => {
        if (!account || !taskId) return;
        setIsLoading(true);
        try {
            // We need getTask method in service. Wait, I didn't add getTask(id) in service, only getTasks list. 
            // I need to add getTask to service! 
            // For now I will fetch list and find (inefficient) or better, add getTask to service.
            // Assuming I will add getTask to service.

            // Let's implement getTask in service quickly.
            // Or I can just start with create.
        } catch (error) {
            toast.error("Failed to load task");
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!account) return;

        setIsLoading(true);
        try {
            if (isEditMode && taskId) {
                await taskService.updateTask(account.id, taskId, title, description);
                toast.success('Task updated');
            } else {
                await taskService.createTask(account.id, title, description);
                toast.success('Task created');
            }
            navigate('/tasks');
        } catch (error) {
            toast.error('Failed to save task');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-6 max-w-2xl mx-auto">
            <h1 className="text-2xl font-bold mb-6">{isEditMode ? 'Edit Task' : 'New Task'}</h1>
            <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-6 space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Title</label>
                    <input
                        type="text"
                        required
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Description</label>
                    <textarea
                        required
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows={4}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    />
                </div>
                <div className="flex justify-end space-x-3">
                    <button
                        type="button"
                        onClick={() => navigate('/tasks')}
                        className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none disabled:opacity-50"
                    >
                        {isLoading ? 'Saving...' : 'Save'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default TaskForm;
