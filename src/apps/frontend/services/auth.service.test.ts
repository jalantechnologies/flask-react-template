import { describe, expect, it, vi } from 'vitest';

import AuthService from 'frontend/services/auth.service';
import { PhoneNumber } from 'frontend/types';

const { post } = vi.hoisted(() => ({ post: vi.fn() }));

vi.mock('axios', () => ({
  default: { create: () => ({ post }) },
}));

describe('AuthService', () => {
  it('posts credentials and returns an AccessToken built from the response', async () => {
    post.mockResolvedValue({
      data: {
        account_id: 'acc-1',
        token: 'jwt-123',
        expires_at: '2999-01-01T00:00:00Z',
      },
    });

    const response = await new AuthService().login(
      'user@example.com',
      'secret',
    );

    expect(post).toHaveBeenCalledWith('/access-tokens', {
      username: 'user@example.com',
      password: 'secret',
    });
    expect(response.data?.accountId).toBe('acc-1');
    expect(response.data?.token).toBe('jwt-123');
  });

  it('sends the phone number payload when verifying an OTP', async () => {
    post.mockResolvedValue({
      data: { account_id: 'acc-2', token: 'jwt-456', expires_at: '2999-01-01' },
    });

    const phoneNumber = new PhoneNumber({
      country_code: '+1',
      phone_number: '5551234567',
    });
    const response = await new AuthService().verifyOTP(phoneNumber, '1234');

    expect(post).toHaveBeenCalledWith('/access-tokens', {
      phone_number: { country_code: '+1', phone_number: '5551234567' },
      otp_code: '1234',
    });
    expect(response.data?.token).toBe('jwt-456');
  });

  it('propagates a rejected request to the caller', async () => {
    post.mockRejectedValue(new Error('network down'));

    await expect(
      new AuthService().login('user@example.com', 'secret'),
    ).rejects.toThrow('network down');
  });
});
