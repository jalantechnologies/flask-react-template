import APIService from 'frontend/services/api.service';
import { ApiResponse, Task } from 'frontend/types';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

export default class TaskService extends APIService {
    constructor() {
        super();
        this.apiClient.interceptors.request.use((config: any) => {
            const tokenObj = getAccessTokenFromStorage();
            if (tokenObj && tokenObj.token) {
                config.headers.Authorization = `Bearer ${tokenObj.token}`;
            }
            return config;
        });
    }

    getTasks = async (accountId: string, page: number = 1, size: number = 10): Promise<ApiResponse<Task[]>> =>
        this.apiClient.get(`/accounts/${accountId}/tasks`, {
            params: { page, size },
        });

    createTask = async (accountId: string, title: string, description: string): Promise<ApiResponse<Task>> =>
        this.apiClient.post(`/accounts/${accountId}/tasks`, {
            title,
            description,
        });

    updateTask = async (
        accountId: string,
        taskId: string,
        title: string,
        description: string
    ): Promise<ApiResponse<Task>> =>
        this.apiClient.patch(`/accounts/${accountId}/tasks/${taskId}`, {
            title,
            description,
        });

    deleteTask = async (accountId: string, taskId: string): Promise<ApiResponse<void>> =>
        this.apiClient.delete(`/accounts/${accountId}/tasks/${taskId}`);
}
