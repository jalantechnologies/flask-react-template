import { describe, expect, it, vi } from 'vitest';

import ApiKeyService from 'frontend/services/api-key.service';
import { AccessToken } from 'frontend/types';

const { get, post, del } = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  del: vi.fn(),
}));

vi.mock('axios', () => ({
  default: { create: () => ({ get, post, delete: del }) },
}));

const accessToken = new AccessToken({
  account_id: 'acc-1',
  token: 'jwt-123',
  expires_at: '2999-01-01',
});

describe('ApiKeyService', () => {
  it('lists keys for the account and maps each into an ApiKey model', async () => {
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

    const response = await new ApiKeyService().listApiKeys(accessToken);

    expect(get).toHaveBeenCalledWith('/accounts/acc-1/api-keys', {
      headers: { Authorization: 'Bearer jwt-123' },
    });
    expect(response.data).toHaveLength(1);
    expect(response.data?.[0].name).toBe('Deploy Bot');
    expect(response.data?.[0].status).toBe('active');
  });

  it('creates a key and returns the show-once plaintext secret', async () => {
    post.mockResolvedValue({
      data: {
        id: 'key-2',
        account_id: 'acc-1',
        name: 'CI',
        status: 'active',
        key: 'frt_secret_value',
      },
    });

    const response = await new ApiKeyService().createApiKey(accessToken, {
      name: 'CI',
      expiresInDays: 30,
    });

    expect(post).toHaveBeenCalledWith(
      '/accounts/acc-1/api-keys',
      { name: 'CI', expires_in_days: 30 },
      { headers: { Authorization: 'Bearer jwt-123' } },
    );
    expect(response.data?.plaintextKey).toBe('frt_secret_value');
    expect(response.data?.apiKey.id).toBe('key-2');
  });

  it('omits expiry from the payload when none is given', async () => {
    post.mockResolvedValue({
      data: {
        id: 'key-3',
        account_id: 'acc-1',
        name: 'No expiry',
        status: 'active',
        key: 'frt_x',
      },
    });

    await new ApiKeyService().createApiKey(accessToken, {
      name: 'No expiry',
    });

    expect(post).toHaveBeenCalledWith(
      '/accounts/acc-1/api-keys',
      { name: 'No expiry' },
      { headers: { Authorization: 'Bearer jwt-123' } },
    );
  });

  it('revokes a key by id', async () => {
    del.mockResolvedValue({ data: undefined });

    await new ApiKeyService().revokeApiKey(accessToken, 'key-1');

    expect(del).toHaveBeenCalledWith('/accounts/acc-1/api-keys/key-1', {
      headers: { Authorization: 'Bearer jwt-123' },
    });
  });
});
