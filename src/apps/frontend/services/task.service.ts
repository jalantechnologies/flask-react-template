import APIService from 'frontend/services/api.service';
import { ApiResponse } from 'frontend/types';
import { JsonObject } from 'frontend/types/common-types';
import { Comment, PaginationResult, PaginationParams, Task } from 'frontend/types/task';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

export default class TaskService extends APIService {

    // Helper to get headers
    private getHeaders() {
        const token = getAccessTokenFromStorage();
        if (token) {
            return { Authorization: `Bearer ${token.token}` };
        }
        return {};
    }

    // TASK APIs

    getTasks = async (page: number = 1, size: number = 10): Promise<ApiResponse<PaginationResult<Task>>> => {
        const token = getAccessTokenFromStorage();
        if (!token) throw new Error('No access token found');

        const response = await this.apiClient.get<JsonObject>(`/accounts/${token.accountId}/tasks`, {
            params: { page, size },
            headers: this.getHeaders(),
        });

        const items = (response.data.items as JsonObject[]).map((item) => new Task(item));
        const paginationParams = new PaginationParams(response.data.pagination_params as JsonObject);
        const totalCount = response.data.total_count as number;

        return new ApiResponse(new PaginationResult(items, paginationParams, totalCount));
    };

    createTask = async (title: string, description: string): Promise<ApiResponse<Task>> => {
        const token = getAccessTokenFromStorage();
        if (!token) throw new Error('No access token found');

        const response = await this.apiClient.post<JsonObject>(
            `/accounts/${token.accountId}/tasks`,
            { title, description },
            { headers: this.getHeaders() }
        );

        return new ApiResponse(new Task(response.data));
    };

    updateTask = async (taskId: string, title: string, description: string): Promise<ApiResponse<Task>> => {
        const token = getAccessTokenFromStorage();
        if (!token) throw new Error('No access token found');

        const response = await this.apiClient.patch<JsonObject>(
            `/accounts/${token.accountId}/tasks/${taskId}`,
            { title, description },
            { headers: this.getHeaders() }
        );

        return new ApiResponse(new Task(response.data));
    };

    deleteTask = async (taskId: string): Promise<ApiResponse<void>> => {
        const token = getAccessTokenFromStorage();
        if (!token) throw new Error('No access token found');

        await this.apiClient.delete(
            `/accounts/${token.accountId}/tasks/${taskId}`,
            { headers: this.getHeaders() }
        );

        return new ApiResponse();
    };

    // COMMENT APIs

    getComments = async (taskId: string, page: number = 1, size: number = 10): Promise<ApiResponse<PaginationResult<Comment>>> => {
        const token = getAccessTokenFromStorage();
        if (!token) throw new Error('No access token found');

        const response = await this.apiClient.get<JsonObject>(
            `/accounts/${token.accountId}/tasks/${taskId}/comments`,
            {
                params: { page, size },
                headers: this.getHeaders(),
            }
        );

        const items = (response.data.items as JsonObject[]).map((item) => new Comment(item));
        const paginationParams = new PaginationParams(response.data.pagination_params as JsonObject);
        const totalCount = response.data.total_count as number;

        return new ApiResponse(new PaginationResult(items, paginationParams, totalCount));
    };

    createComment = async (taskId: string, content: string): Promise<ApiResponse<Comment>> => {
        const token = getAccessTokenFromStorage();
        if (!token) throw new Error('No access token found');

        const response = await this.apiClient.post<JsonObject>(
            `/accounts/${token.accountId}/tasks/${taskId}/comments`,
            { content },
            { headers: this.getHeaders() }
        );

        return new ApiResponse(new Comment(response.data));
    };

    updateComment = async (commentId: string, content: string): Promise<ApiResponse<Comment>> => {
        const token = getAccessTokenFromStorage();
        if (!token) throw new Error('No access token found');

        const response = await this.apiClient.patch<JsonObject>(
            `/accounts/${token.accountId}/comments/${commentId}`,
            { content },
            { headers: this.getHeaders() }
        );

        return new ApiResponse(new Comment(response.data));
    };

    deleteComment = async (commentId: string): Promise<ApiResponse<void>> => {
        const token = getAccessTokenFromStorage();
        if (!token) throw new Error('No access token found');

        await this.apiClient.delete(
            `/accounts/${token.accountId}/comments/${commentId}`,
            { headers: this.getHeaders() }
        );

        return new ApiResponse();
    };
}
