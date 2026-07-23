import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React, { PropsWithChildren } from 'react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ResetPasswordProvider } from 'frontend/contexts/reset-password.provider';
import ResetPasswordForm from 'frontend/pages/authentication/reset-password/reset-password-form';
import { AsyncError } from 'frontend/types';

const { patch } = vi.hoisted(() => ({ patch: vi.fn() }));

vi.mock('axios', () => ({
  default: { create: () => ({ patch }) },
}));

beforeEach(() => {
  localStorage.clear();
  patch.mockReset();
});

const renderForm = (props: {
  onError: (error: AsyncError) => void;
  onSuccess: () => void;
}) => {
  const wrapper = ({ children }: PropsWithChildren) => (
    <MemoryRouter initialEntries={['/accounts/acc-1/reset-password?token=tok']}>
      <ResetPasswordProvider>
        <Routes>
          <Route
            path="/accounts/:accountId/reset-password"
            element={children}
          />
        </Routes>
      </ResetPasswordProvider>
    </MemoryRouter>
  );

  return render(
    <ResetPasswordForm onSuccess={props.onSuccess} onError={props.onError} />,
    { wrapper },
  );
};

describe('ResetPasswordForm', () => {
  it('shows a weak rating and blocks submission for a guessable password', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    const onError = vi.fn();

    renderForm({ onSuccess, onError });

    await user.type(screen.getByTestId('password'), 'password');
    await user.type(screen.getByTestId('confirmPassword'), 'password');

    expect(screen.getByTestId('password-strength-label')).toHaveTextContent(
      'Very weak',
    );

    await user.click(screen.getByRole('button', { name: 'Reset Password' }));

    expect(
      await screen.findByText(
        'Please choose a stronger password. Add length and avoid common words or predictable patterns.',
      ),
    ).toBeInTheDocument();
    expect(patch).not.toHaveBeenCalled();
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it('submits when the password is strong enough', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    const onError = vi.fn();
    patch.mockResolvedValue({ data: {} });

    renderForm({ onSuccess, onError });

    await user.type(
      screen.getByTestId('password'),
      'correct horse battery staple 12',
    );
    await user.type(
      screen.getByTestId('confirmPassword'),
      'correct horse battery staple 12',
    );

    expect(screen.getByTestId('password-strength-label')).toHaveTextContent(
      'Very strong',
    );

    await user.click(screen.getByRole('button', { name: 'Reset Password' }));

    await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1));
    expect(patch).toHaveBeenCalledWith('/accounts/acc-1', {
      new_password: 'correct horse battery staple 12',
      token: 'tok',
    });
  });
});
