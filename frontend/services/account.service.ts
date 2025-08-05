import APIService from 'frontend/services/api.service';
import { Account, AccessToken, ApiResponse } from 'frontend/types';

export default class AccountService extends APIService {
  getAccountDetails = async (
    userAccessToken: AccessToken,
  ): Promise<ApiResponse<Account>> =>
    this.apiClient.get(`/accounts/${userAccessToken.accountId}`, {
      headers: {
        Authorization: `Bearer ${userAccessToken.token}`,
      },
    });
}
