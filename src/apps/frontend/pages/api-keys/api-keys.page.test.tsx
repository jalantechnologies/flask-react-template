import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React, { PropsWithChildren } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import ApiKeysPage from 'frontend/pages/api-keys/api-keys.page';

const { get, post, del } = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  del: vi.fn(),
}));

vi.mock('axios', () => ({
  default: { create: () => ({ get, post, delete: del }) },
}));

vi.mock('react-hot-toast', () => ({
  default: { success: vi.fn(), error: vi.fn() },
}));

const seedToken = () => {
  localStorage.setItem(
    'access-token',
    JSON.stringify({
      account_id: 'acc-1',
      token: 'jwt-123',
      expires_at: '2999-01-01',
    }),
  );
};

const wrapper = ({ children }: PropsWithChildren) => (
  <MemoryRouter>{children}</MemoryRouter>
);

beforeEach(() => {
  localStorage.clear();
  get.mockReset();
  post.mockReset();
  del.mockReset();
  seedToken();
});

describe('ApiKeysPage', () => {
  it('shows the empty state when the account has no keys', async () => {
    get.mockResolvedValue({ data: { items: [] } });

    render(<ApiKeysPage />, { wrapper });

    expect(await screen.findByTestId('api-keys-empty')).toBeInTheDocument();
    expect(get).toHaveBeenCalledWith('/accounts/acc-1/api-keys', {
      headers: { Authorization: 'Bearer jwt-123' },
    });
  });

  it('renders the account keys in a table', async () => {
    get.mockResolvedValue({
      data: {
        items: [
          {
            id: 'key-1',
            account_id: 'acc-1',
            name: 'Deploy Bot',
            status: 'active',
            created_at: '2026-01-01T00:00:00Z',
            expires_at: null,
            last_used_at: null,
          },
        ],
      },
    });

    render(<ApiKeysPage />, { wrapper });

    expect(await screen.findByTestId('api-keys-table')).toBeInTheDocument();
    expect(screen.getByText('Deploy Bot')).toBeInTheDocument();
    expect(screen.getByTestId('revoke-key-1')).toBeInTheDocument();
  });

  it('creates a key and reveals the plaintext secret once', async () => {
    const user = userEvent.setup();
    get.mockResolvedValue({ data: { items: [] } });
    post.mockResolvedValue({
      data: {
        id: 'key-9',
        account_id: 'acc-1',
        name: 'CI Bot',
        status: 'active',
        key: 'frt_shown_once_secret',
      },
    });

    render(<ApiKeysPage />, { wrapper });

    await user.click(await screen.findByTestId('create-api-key-button'));
    await user.type(screen.getByTestId('api-key-name-input'), 'CI Bot');
    await user.click(screen.getByTestId('submit-api-key-button'));

    await waitFor(() =>
      expect(screen.getByTestId('api-key-created-modal')).toBeInTheDocument(),
    );
    expect(screen.getByTestId('created-api-key-value')).toHaveValue(
      'frt_shown_once_secret',
    );

    expect(post).toHaveBeenCalledWith(
      '/accounts/acc-1/api-keys',
      { name: 'CI Bot' },
      { headers: { Authorization: 'Bearer jwt-123' } },
    );
  });

  it('revokes a key after confirmation', async () => {
    const user = userEvent.setup();
    get.mockResolvedValue({
      data: {
        items: [
          {
            id: 'key-1',
            account_id: 'acc-1',
            name: 'Deploy Bot',
            status: 'active',
            created_at: '2026-01-01T00:00:00Z',
            expires_at: null,
            last_used_at: null,
          },
        ],
      },
    });
    del.mockResolvedValue({ data: undefined });

    render(<ApiKeysPage />, { wrapper });

    await user.click(await screen.findByTestId('revoke-key-1'));
    const dialog = screen.getByTestId('revoke-confirm-dialog');
    expect(dialog).toBeInTheDocument();

    await user.click(within(dialog).getByRole('button', { name: 'Revoke' }));

    await waitFor(() =>
      expect(del).toHaveBeenCalledWith('/accounts/acc-1/api-keys/key-1', {
        headers: { Authorization: 'Bearer jwt-123' },
      }),
    );
  });
});
