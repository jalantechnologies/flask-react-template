import { describe, expect, it } from 'vitest';

import { AsyncOperationError } from 'frontend/types/async-operation';

const FALLBACK = 'Something went wrong. Please try again.';

describe('AsyncOperationError.fromUnknown', () => {
  it('prefers the code and message carried on an axios error response body', () => {
    const thrown = {
      code: 'ERR_BAD_REQUEST',
      message: 'Request failed with status code 401',
      response: {
        data: {
          code: 'INVALID_CREDENTIALS',
          message: 'Username or password is incorrect.',
        },
      },
    };

    const error = AsyncOperationError.fromUnknown(thrown, FALLBACK);

    expect(error.code).toBe('INVALID_CREDENTIALS');
    expect(error.message).toBe('Username or password is incorrect.');
  });

  it('falls back to the top level axios code when the response body carries none', () => {
    const thrown = {
      code: 'ERR_NETWORK',
      message: 'Network Error',
      response: { data: {} },
    };

    const error = AsyncOperationError.fromUnknown(thrown, FALLBACK);

    expect(error.code).toBe('ERR_NETWORK');
    expect(error.message).toBe('Network Error');
  });

  it('reads a plain Error message and leaves the code unset', () => {
    const error = AsyncOperationError.fromUnknown(new Error('Boom'), FALLBACK);

    expect(error.code).toBeUndefined();
    expect(error.message).toBe('Boom');
  });

  it('adopts a thrown string as the message', () => {
    const error = AsyncOperationError.fromUnknown('Just a string', FALLBACK);

    expect(error.code).toBeUndefined();
    expect(error.message).toBe('Just a string');
  });

  it('uses the fallback message when nothing usable was thrown', () => {
    expect(AsyncOperationError.fromUnknown(undefined, FALLBACK).message).toBe(
      FALLBACK,
    );
    expect(AsyncOperationError.fromUnknown(null, FALLBACK).message).toBe(
      FALLBACK,
    );
    expect(AsyncOperationError.fromUnknown({}, FALLBACK).message).toBe(
      FALLBACK,
    );
    expect(AsyncOperationError.fromUnknown(42, FALLBACK).message).toBe(
      FALLBACK,
    );
  });

  it('ignores non-string code and message fields', () => {
    const error = AsyncOperationError.fromUnknown(
      { code: 500, message: { nested: true } },
      FALLBACK,
    );

    expect(error.code).toBeUndefined();
    expect(error.message).toBe(FALLBACK);
  });

  it('ignores an empty string code so the outer code still wins', () => {
    const thrown = {
      code: 'ERR_BAD_RESPONSE',
      response: { data: { code: '' } },
    };

    expect(AsyncOperationError.fromUnknown(thrown, FALLBACK).code).toBe(
      'ERR_BAD_RESPONSE',
    );
  });

  it('produces an instance that satisfies the AsyncError shape', () => {
    const error = AsyncOperationError.fromUnknown(new Error('Boom'), FALLBACK);

    expect(error).toBeInstanceOf(AsyncOperationError);
  });
});
