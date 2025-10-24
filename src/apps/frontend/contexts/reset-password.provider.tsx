import React, { createContext, PropsWithChildren, useContext } from 'react';

import useAsync from 'frontend/contexts/async.hook';
import { ResetPasswordParams } from 'frontend/pages/authentication/reset-password/reset-password-form.hook';
import { ResetPasswordService } from 'frontend/services';
import { ApiResponse, AsyncError } from 'frontend/types';
import { Nullable } from 'frontend/types/common-types';

type ResetPasswordContextType = {
  isResetPasswordLoading: boolean;
  isSendForgotPasswordEmailLoading: boolean;
  resetPassword: (params: ResetPasswordParams) => Promise<Nullable<void>>;
  resetPasswordError: Nullable<AsyncError>;
  sendForgotPasswordEmail: (username: string) => Promise<Nullable<void>>;
  sendForgotPasswordEmailError: Nullable<AsyncError>;
};

const ResetPasswordContext =
  createContext<Nullable<ResetPasswordContextType>>(null);

const resetPasswordService = new ResetPasswordService();

export const useResetPasswordContext = (): ResetPasswordContextType =>
  useContext(ResetPasswordContext) as ResetPasswordContextType;

const resetPasswordFn = async (
  params: ResetPasswordParams,
): Promise<ApiResponse<void>> => resetPasswordService.resetPassword(params);

const sendForgotPasswordEmailFn = async (
  username: string,
): Promise<ApiResponse<void>> =>
  resetPasswordService.sendForgotPasswordEmail(username);

export const ResetPasswordProvider: React.FC<PropsWithChildren> = ({
  children,
}) => {
  const {
    isLoading: isSendForgotPasswordEmailLoading,
    error: sendForgotPasswordEmailError,
    asyncCallback: sendForgotPasswordEmail,
  } = useAsync(sendForgotPasswordEmailFn);

  const {
    isLoading: isResetPasswordLoading,
    error: resetPasswordError,
    asyncCallback: resetPassword,
  } = useAsync(resetPasswordFn);

  return (
    <ResetPasswordContext.Provider
      value={{
        isResetPasswordLoading,
        isSendForgotPasswordEmailLoading,
        resetPassword,
        resetPasswordError,
        sendForgotPasswordEmail,
        sendForgotPasswordEmailError,
      }}
    >
      {children}
    </ResetPasswordContext.Provider>
  );
};
