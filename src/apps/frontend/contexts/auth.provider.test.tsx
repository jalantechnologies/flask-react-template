import {
  act,
  render,
  renderHook,
  screen,
  waitFor,
} from '@testing-library/react';
import React, { PropsWithChildren } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider, useAuthContext } from 'frontend/contexts/auth.provider';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

const { post } = vi.hoisted(() => ({ post: vi.fn() }));

vi.mock('axios', () => ({
  default: { create: () => ({ post }) },
}));

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  localStorage.clear();
});

const wrapper = ({ children }: PropsWithChildren) => (
  <AuthProvider>{children}</AuthProvider>
);

const SessionProbe: React.FC = () => {
  const { isUserAuthenticated } = useAuthContext();
  return (
    <span data-testid="auth-state">
      {isUserAuthenticated() ? 'authenticated' : 'anonymous'}
    </span>
  );
};

describe('AuthProvider', () => {
  it('starts unauthenticated when storage holds no token', () => {
    const { result } = renderHook(() => useAuthContext(), { wrapper });

    expect(result.current.isUserAuthenticated()).toBe(false);
  });

  it('persists the token and becomes authenticated after a successful login', async () => {
    post.mockResolvedValue({
      data: {
        account_id: 'acc-1',
        token: 'jwt-123',
        expires_at: '2999-01-01T00:00:00Z',
      },
    });

    const { result } = renderHook(() => useAuthContext(), { wrapper });

    await act(async () => {
      await result.current.login('user@example.com', 'secret');
    });

    expect(result.current.isUserAuthenticated()).toBe(true);
    expect(getAccessTokenFromStorage()?.token).toBe('jwt-123');
  });

  it('does not authenticate and surfaces the error when login fails', async () => {
    post.mockRejectedValue(new Error('bad credentials'));

    const { result } = renderHook(() => useAuthContext(), { wrapper });

    await act(async () => {
      await expect(
        result.current.login('user@example.com', 'wrong'),
      ).rejects.toThrow();
    });

    expect(result.current.isUserAuthenticated()).toBe(false);
    expect(getAccessTokenFromStorage()).toBeNull();
    await waitFor(() => expect(result.current.loginError).not.toBeNull());
  });

  it('clears the session on logout', async () => {
    post.mockResolvedValue({
      data: { account_id: 'acc-1', token: 'jwt-123', expires_at: '2999-01-01' },
    });

    const { result } = renderHook(() => useAuthContext(), { wrapper });

    await act(async () => {
      await result.current.login('user@example.com', 'secret');
    });
    expect(result.current.isUserAuthenticated()).toBe(true);

    act(() => {
      result.current.logout();
    });

    expect(result.current.isUserAuthenticated()).toBe(false);
    expect(getAccessTokenFromStorage()).toBeNull();
  });

  it('seeds an authenticated session from a token already in storage', () => {
    localStorage.setItem(
      'access-token',
      JSON.stringify({
        account_id: 'acc-9',
        token: 'stored',
        expires_at: '2999-01-01',
      }),
    );

    render(
      <AuthProvider>
        <SessionProbe />
      </AuthProvider>,
    );

    expect(screen.getByTestId('auth-state')).toHaveTextContent('authenticated');
  });
});
