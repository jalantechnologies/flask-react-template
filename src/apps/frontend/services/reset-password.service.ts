import { ResetPasswordParams } from 'frontend/pages/authentication/reset-password/reset-password-form.hook';
import APIService from 'frontend/services/api.service';
import { ApiResponse } from 'frontend/types';

export default class ResetPasswordService extends APIService {
  sendForgotPasswordEmail = async (
    username: string,
  ): Promise<ApiResponse<void>> =>
    this.apiClient.post('/password-reset-tokens', {
      username,
    });

  resetPassword = async (
    params: ResetPasswordParams,
  ): Promise<ApiResponse<void>> => {
    const { accountId, newPassword, token } = params;
    return this.apiClient.patch(`/accounts/${accountId}`, {
      new_password: newPassword,
      token,
    });
  };
}
