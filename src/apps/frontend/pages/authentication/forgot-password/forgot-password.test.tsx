import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React, { PropsWithChildren } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import constant from 'frontend/constants';
import { ResetPasswordProvider } from 'frontend/contexts/reset-password.provider';
import ForgotPassword from 'frontend/pages/authentication/forgot-password';

const { post } = vi.hoisted(() => ({ post: vi.fn() }));

vi.mock('axios', () => ({
  default: { create: () => ({ post }) },
}));

const KNOWN_EMAIL = 'known@example.com';
const UNKNOWN_EMAIL = 'unknown@example.com';

const NEUTRAL_API_RESPONSE = {
  data: {
    message: 'If an account exists for that email, a reset link has been sent.',
  },
};

beforeEach(() => {
  post.mockReset();
  localStorage.clear();
});

const renderForgotPassword = () => {
  const wrapper = ({ children }: PropsWithChildren) => (
    <MemoryRouter>
      <ResetPasswordProvider>{children}</ResetPasswordProvider>
    </MemoryRouter>
  );

  return render(<ForgotPassword />, { wrapper });
};

const submitEmail = async (email: string) => {
  const user = userEvent.setup();
  await user.type(screen.getByTestId('username'), email);
  await user.click(screen.getByRole('button', { name: 'Receive Reset Link' }));
};

describe('ForgotPassword', () => {
  it('shows the neutral confirmation after requesting a reset link', async () => {
    post.mockResolvedValue(NEUTRAL_API_RESPONSE);

    renderForgotPassword();
    await submitEmail(KNOWN_EMAIL);

    expect(
      await screen.findByText(constant.PASSWORD_RESET_LINK_SENT_MESSAGE),
    ).toBeInTheDocument();
    expect(post).toHaveBeenCalledWith('/password-reset-tokens', {
      username: KNOWN_EMAIL,
    });
  });

  it('shows the same confirmation for an address with no account', async () => {
    post.mockResolvedValue(NEUTRAL_API_RESPONSE);

    renderForgotPassword();
    await submitEmail(UNKNOWN_EMAIL);

    expect(
      await screen.findByText(constant.PASSWORD_RESET_LINK_SENT_MESSAGE),
    ).toBeInTheDocument();
  });

  it('does not reveal whether the submitted address has an account', async () => {
    post.mockResolvedValue(NEUTRAL_API_RESPONSE);

    renderForgotPassword();
    await submitEmail(KNOWN_EMAIL);

    await screen.findByText(constant.PASSWORD_RESET_LINK_SENT_MESSAGE);

    expect(screen.queryByText(new RegExp(KNOWN_EMAIL, 'i'))).toBeNull();
    expect(screen.queryByText(/has been sent to/i)).toBeNull();
  });

  it('reports the failure when the request is rejected', async () => {
    post.mockRejectedValue({
      response: { data: { message: 'Something went wrong', code: 'ERR' } },
    });

    renderForgotPassword();
    await submitEmail(KNOWN_EMAIL);

    await waitFor(() => expect(post).toHaveBeenCalledTimes(1));
    expect(
      screen.queryByText(constant.PASSWORD_RESET_LINK_SENT_MESSAGE),
    ).toBeNull();
  });
});
