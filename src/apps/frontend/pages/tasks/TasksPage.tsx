import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { Link } from 'react-router-dom';

import { useAccountContext } from 'frontend/contexts';
import TaskService from 'frontend/services/task.service';
import { Task } from 'frontend/types/task';

const TasksPage: React.FC = () => {
    const { account } = useAccountContext();
    const [tasks, setTasks] = useState<Task[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const taskService = new TaskService();

    useEffect(() => {
        if (account) {
            loadTasks();
        }
    }, [account]);

    const loadTasks = async () => {
        if (!account) return;
        setIsLoading(true);
        try {
            const response = await taskService.getTasks(account.id);
            if (response.data) {
                setTasks(response.data);
            }
        } catch (error) {
            toast.error('Failed to load tasks');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (taskId: string) => {
        if (!account) return;
        if (!window.confirm("Are you sure?")) return;

        try {
            await taskService.deleteTask(account.id, taskId);
            toast.success("Task deleted");
            loadTasks();
        } catch (e) {
            toast.error("Failed to delete task");
        }
    };

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Tasks</h1>
                <Link to="/tasks/new" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Add Task
                </Link>
            </div>

            {isLoading ? (
                <div>Loading...</div>
            ) : (
                <div className="bg-white shadow rounded-lg overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {tasks.map((task) => (
                                <tr key={task.id}>
                                    <td className="px-6 py-4 whitespace-nowrap">{task.title}</td>
                                    <td className="px-6 py-4">{task.description}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <Link to={`/tasks/${task.id}/edit`} className="text-indigo-600 hover:text-indigo-900 mr-4">Edit</Link>
                                        <button onClick={() => handleDelete(task.id)} className="text-red-600 hover:text-red-900">Delete</button>
                                    </td>
                                </tr>
                            ))}
                            {tasks.length === 0 && (
                                <tr>
                                    <td colSpan={3} className="px-6 py-4 text-center text-gray-500">No tasks found</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default TasksPage;
