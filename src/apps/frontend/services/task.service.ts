import APIService from 'frontend/services/api.service';
import { AccessToken, ApiResponse, PhoneNumber } from 'frontend/types';
import { JsonObject } from 'frontend/types/common-types';
import { Task } from 'frontend/types/tasks';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

export default class TaskService extends APIService {
  private static getAccountID(): string {
    const tokenString = localStorage.getItem('access-token');
    if (!tokenString) {
      throw new Error('No access token found. Please login.');
    }

    try {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unsafe-assignment
      const accountID = JSON.parse(tokenString)?.account_id;
      if (!accountID) {
        throw new Error('Account ID not found in token. Please login again.');
      }
      // eslint-disable-next-line @typescript-eslint/no-unsafe-return
      return accountID;
    } catch (error) {
      throw new Error('Invalid access token format. Please login again.');
    }
  }

  createTasks = async (
    title: string,
    description: string,
  ): Promise<ApiResponse<void>> =>
    this.apiClient.post(
      `/accounts/${TaskService.getAccountID()}/tasks`,
      {
        title,
        description,
      },
      {
        headers: {
          Authorization: `Bearer ${getAccessTokenFromStorage()?.token}`,
        },
      },
    );
  deleteTasks = async (taskId: string): Promise<ApiResponse<void>> => {
    console.log('TaskID', taskId);
    return this.apiClient.delete(
      `/accounts/${TaskService.getAccountID()}/tasks/${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${getAccessTokenFromStorage()?.token}`,
        },
      },
    );
  };

  getTasks = async (): Promise<ApiResponse<Task[]>> => {
    const response = await this.apiClient.get<JsonObject>(
      `/accounts/${TaskService.getAccountID()}/tasks`,
      {
        headers: {
          Authorization: `Bearer ${getAccessTokenFromStorage()?.token}`,
        },
      },
    );
    const tasksArray = (response.data as any).items || [];
    const tasks = tasksArray.map((taskData: any) => new Task(taskData));
    console.log(
      ' I am printing here the taskArray and tasks',
      tasks,
      tasksArray,
      response,
    );
    return new ApiResponse(tasks);
  };

  sendOTP = async (phoneNumber: PhoneNumber): Promise<ApiResponse<void>> =>
    this.apiClient.post('/accounts', {
      phone_number: {
        country_code: phoneNumber.countryCode,
        phone_number: phoneNumber.phoneNumber,
      },
    });

  verifyOTP = async (
    phoneNumber: PhoneNumber,
    otp: string,
  ): Promise<ApiResponse<AccessToken>> => {
    const response = await this.apiClient.post<JsonObject>('/access-tokens', {
      phone_number: {
        country_code: phoneNumber.countryCode,
        phone_number: phoneNumber.phoneNumber,
      },
      otp_code: otp,
    });
    return new ApiResponse(new AccessToken(response.data));
  };
}
