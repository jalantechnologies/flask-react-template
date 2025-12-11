import React, { createContext, PropsWithChildren, useContext, useState, useEffect } from 'react';

import useAsync from 'frontend/contexts/async.hook';
import { AuthService } from 'frontend/services';
import {
  AccessToken,
  ApiResponse,
  AsyncError,
  PhoneNumber,
} from 'frontend/types';
import { Nullable } from 'frontend/types/common-types';
import {
  getAccessTokenFromStorage,
  removeAccessTokenFromStorage,
  setAccessTokenToStorage,
} from 'frontend/utils/storage-util';

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
  sendOTP: (phoneNumber: PhoneNumber) => Promise<Nullable<void>>;
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

const isUserAuthenticated = () => !!getAccessTokenFromStorage();

const sendOTPFn = async (
  phoneNumber: PhoneNumber,
): Promise<ApiResponse<void>> => authService.sendOTP(phoneNumber);

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

export const AuthProvider: React.FC<PropsWithChildren> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(isUserAuthenticated);

  useEffect(() => {
    setIsAuthenticated(isUserAuthenticated());
  }, []);

  const logout = (): void => {
    removeAccessTokenFromStorage();
    setIsAuthenticated(false);
  };

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
  } = useAsync(async (username: string, password: string) => {
    const result = await loginFn(username, password);
    if (result.data) {
      setIsAuthenticated(true);
    }
    return result;
  });

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
  } = useAsync(async (phoneNumber: PhoneNumber, otp: string) => {
    const result = await verifyOTPFn(phoneNumber, otp);
    if (result.data) {
      setIsAuthenticated(true);
    }
    return result;
  });

  return (
    <AuthContext.Provider
      value={{
        isLoginLoading,
        isSendOTPLoading,
        isSignupLoading,
        isUserAuthenticated: () => isAuthenticated,
        isVerifyOTPLoading,
        login,
        loginError,
        loginResult,
        logout,
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
