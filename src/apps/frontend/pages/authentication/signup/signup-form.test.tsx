import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React, { PropsWithChildren } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from 'frontend/contexts/auth.provider';
import SignupForm from 'frontend/pages/authentication/signup/signup-form';
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
    <SignupForm onSuccess={props.onSuccess} onError={props.onError} />,
    { wrapper },
  );
};

const fillIdentity = async (user: ReturnType<typeof userEvent.setup>) => {
  await user.type(screen.getByTestId('firstName'), 'Ada');
  await user.type(screen.getByTestId('lastName'), 'Lovelace');
  await user.type(screen.getByTestId('username'), 'ada@example.com');
};

describe('SignupForm', () => {
  it('shows a weak rating and blocks submission for a guessable password', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    const onError = vi.fn();

    renderForm({ onSuccess, onError });

    await fillIdentity(user);
    await user.type(screen.getByTestId('password'), 'password');
    await user.type(screen.getByTestId('retypePassword'), 'password');

    expect(screen.getByTestId('password-strength-label')).toHaveTextContent(
      'Very weak',
    );

    await user.click(screen.getByRole('button', { name: 'Sign Up' }));

    expect(
      await screen.findByText(
        'Please choose a stronger password. Add length and avoid common words or predictable patterns.',
      ),
    ).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it('submits when the password is strong enough', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    const onError = vi.fn();
    post.mockResolvedValue({ data: { id: 'acc-1' } });

    renderForm({ onSuccess, onError });

    await fillIdentity(user);
    await user.type(
      screen.getByTestId('password'),
      'correct horse battery staple 12',
    );
    await user.type(
      screen.getByTestId('retypePassword'),
      'correct horse battery staple 12',
    );

    expect(screen.getByTestId('password-strength-label')).toHaveTextContent(
      'Very strong',
    );

    await user.click(screen.getByRole('button', { name: 'Sign Up' }));

    await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1));
    expect(post).toHaveBeenCalledWith('/accounts', {
      first_name: 'Ada',
      last_name: 'Lovelace',
      username: 'ada@example.com',
      password: 'correct horse battery staple 12',
    });
  });
});
