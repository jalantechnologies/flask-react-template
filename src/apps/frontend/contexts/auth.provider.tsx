import React, {
  createContext,
  PropsWithChildren,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react';

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

const logoutFn = (): void => removeAccessTokenFromStorage();

const isTokenInStorage = (): boolean => !!getAccessTokenFromStorage();

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
  // Authentication is React state, not a bare storage read, so the router and
  // any consumer re-render the moment a session begins or ends. It is seeded
  // from storage on mount to keep an existing session across reloads.
  const [isAuthenticated, setIsAuthenticated] =
    useState<boolean>(isTokenInStorage);

  const {
    asyncCallback: signup,
    error: signupError,
    isLoading: isSignupLoading,
  } = useAsync(signupFn);

  const {
    isLoading: isLoginLoading,
    error: loginError,
    result: loginResult,
    asyncCallback: loginCallback,
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
    asyncCallback: verifyOTPCallback,
  } = useAsync(verifyOTPFn);

  // loginFn / verifyOTPFn persist the token; flip the reactive flag once the
  // token is in storage so protected routes become reachable immediately.
  const login = useCallback(
    async (username: string, password: string) => {
      const result = await loginCallback(username, password);
      if (result) {
        setIsAuthenticated(true);
      }
      return result;
    },
    [loginCallback],
  );

  const verifyOTP = useCallback(
    async (phoneNumber: PhoneNumber, otp: string) => {
      const result = await verifyOTPCallback(phoneNumber, otp);
      if (result) {
        setIsAuthenticated(true);
      }
      return result;
    },
    [verifyOTPCallback],
  );

  const logout = useCallback(() => {
    logoutFn();
    setIsAuthenticated(false);
  }, []);

  const isUserAuthenticated = useCallback(
    () => isAuthenticated,
    [isAuthenticated],
  );

  const value = useMemo(
    () => ({
      isLoginLoading,
      isSendOTPLoading,
      isSignupLoading,
      isUserAuthenticated,
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
    }),
    [
      isLoginLoading,
      isSendOTPLoading,
      isSignupLoading,
      isUserAuthenticated,
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
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
