import React, {
  createContext,
  PropsWithChildren,
  ReactNode,
  useContext,
} from 'react';

import { AuthService } from '../services';
import { AccessToken, ApiResponse, AsyncError, OTP, PhoneNumber } from '../types';
import { Nullable } from '../types/common-types';
import {
  getAccessTokenFromStorage,
  removeAccessTokenFromStorage,
  setAccessTokenToStorage,
} from '../utils/storage-util';

import useAsync from './async.hook';

type AuthContextType = {
  isLoginLoading: boolean;
  isSendOTPLoading: boolean;
  isSignupLoading: boolean;
  isUserAuthenticated: () => boolean;
  isVerifyOTPLoading: boolean;
  login: (username: string, password: string) => Promise<Nullable<AccessToken>>;
  loginError: Nullable<AsyncError>;
  loginResult: Nullable<AccessToken>;
  logout: () => void;
  sendOTP: (phoneNumber: PhoneNumber) => Promise<Nullable<OTP>>;
  sendOTPError: Nullable<AsyncError>;
  signup: (
    firstName: string,
    lastName: string,
    username: string,
    password: string,
  ) => Promise<Nullable<void>>;
  signupError: Nullable<AsyncError>;
  verifyOTP: (
    phoneNumber: PhoneNumber,
    otp: string,
  ) => Promise<Nullable<AccessToken>>;
  verifyOTPError: Nullable<AsyncError>;
  verifyOTPResult: Nullable<AccessToken>;
};

const AuthContext = createContext<Nullable<AuthContextType>>(null);

const authService = new AuthService();

export const useAuthContext = (): AuthContextType =>
  useContext(AuthContext) as AuthContextType;

const signupFn = async (
  firstName: string,
  lastName: string,
  username: string,
  password: string,
): Promise<ApiResponse<void>> =>
  authService.signup(firstName, lastName, username, password);

const loginFn = async (
  username: string,
  password: string,
): Promise<ApiResponse<AccessToken>> => {
  const result = await authService.login(username, password);
  if (result.data) {
    setAccessTokenToStorage(result.data);
  }
  return result;
};

const logoutFn = (): void => removeAccessTokenFromStorage();

const isUserAuthenticated = () => !!getAccessTokenFromStorage();

const sendOTPFn = async (
  phoneNumber: PhoneNumber,
): Promise<ApiResponse<OTP>> => authService.sendOTP(phoneNumber);

const verifyOTPFn = async (
  phoneNumber: PhoneNumber,
  otp: string,
): Promise<ApiResponse<AccessToken>> => {
  const result = await authService.verifyOTP(phoneNumber, otp);
  if (result.data) {
    setAccessTokenToStorage(result.data);
  }
  return result;
};

export const AuthProvider: React.FC<PropsWithChildren<ReactNode>> = ({
  children,
}) => {
  const {
    asyncCallback: signup,
    error: signupError,
    isLoading: isSignupLoading,
  } = useAsync(signupFn);

  const {
    isLoading: isLoginLoading,
    error: loginError,
    result: loginResult,
    asyncCallback: login,
  } = useAsync(loginFn);

  const {
    isLoading: isSendOTPLoading,
    error: sendOTPError,
    asyncCallback: sendOTP,
  } = useAsync(sendOTPFn);

  const {
    isLoading: isVerifyOTPLoading,
    error: verifyOTPError,
    result: verifyOTPResult,
    asyncCallback: verifyOTP,
  } = useAsync(verifyOTPFn);

  return (
    <AuthContext.Provider
      value={{
        isLoginLoading,
        isSendOTPLoading,
        isSignupLoading,
        isUserAuthenticated,
        isVerifyOTPLoading,
        login,
        loginError,
        loginResult,
        logout: logoutFn,
        sendOTP,
        sendOTPError,
        signup,
        signupError,
        verifyOTP,
        verifyOTPError,
        verifyOTPResult,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
