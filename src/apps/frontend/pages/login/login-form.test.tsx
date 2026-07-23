import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React, { PropsWithChildren } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from 'frontend/contexts/auth.provider';
import LoginForm from 'frontend/pages/login/login-form';
import { AsyncError } from 'frontend/types';

const { post } = vi.hoisted(() => ({ post: vi.fn() }));

vi.mock('axios', () => ({
  default: { create: () => ({ post }) },
}));

beforeEach(() => {
  localStorage.clear();
});

const renderForm = (props: {
  onError: (error: AsyncError) => void;
  onSuccess: () => void;
}) => {
  const wrapper = ({ children }: PropsWithChildren) => (
    <MemoryRouter>
      <AuthProvider>{children}</AuthProvider>
    </MemoryRouter>
  );

  return render(
    <LoginForm onSuccess={props.onSuccess} onError={props.onError} />,
    { wrapper },
  );
};

describe('LoginForm', () => {
  it('blocks submission and shows validation errors for empty fields', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    const onError = vi.fn();

    renderForm({ onSuccess, onError });

    await user.click(screen.getByRole('button', { name: 'Log In' }));

    expect(
      await screen.findByText('Please enter a valid email'),
    ).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it('submits the typed credentials and reports success', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    const onError = vi.fn();
    post.mockResolvedValue({
      data: { account_id: 'acc-1', token: 'jwt-123', expires_at: '2999-01-01' },
    });

    renderForm({ onSuccess, onError });

    await user.type(screen.getByTestId('username'), 'user@example.com');
    await user.type(screen.getByTestId('password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Log In' }));

    await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1));
    expect(post).toHaveBeenCalledWith('/access-tokens', {
      username: 'user@example.com',
      password: 'password123',
    });
    expect(onError).not.toHaveBeenCalled();
  });

  it('reports the failure when the credentials are rejected', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    const onError = vi.fn();
    post.mockRejectedValue({
      response: {
        data: { message: 'Invalid credentials', code: 'UNAUTHORIZED' },
      },
    });

    renderForm({ onSuccess, onError });

    await user.type(screen.getByTestId('username'), 'user@example.com');
    await user.type(screen.getByTestId('password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Log In' }));

    await waitFor(() => expect(onError).toHaveBeenCalledTimes(1));
    expect(onError).toHaveBeenCalledWith(
      expect.objectContaining({ message: 'Invalid credentials' }),
    );
    expect(onSuccess).not.toHaveBeenCalled();
  });
});
