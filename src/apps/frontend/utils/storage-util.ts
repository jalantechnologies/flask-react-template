import { AccessToken } from 'frontend/types';
import { JsonObject, Nullable } from 'frontend/types/common-types';

const ACCESS_TOKEN_KEY = 'access-token';

export const getAccessTokenFromStorage = (): Nullable<AccessToken> => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    return new AccessToken(JSON.parse(token) as JsonObject);
  }
  return null;
};

export const setAccessTokenToStorage = (token: AccessToken): void => {
  localStorage.setItem(ACCESS_TOKEN_KEY, JSON.stringify(token.toJson()));
};

export const removeAccessTokenFromStorage = (): void => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
};
