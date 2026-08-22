import { JsonObject, Nullable } from 'frontend/types/common-types';

export interface AsyncError {
  code?: string;
  message: string;
}

export interface AsyncResult<T> {
  error?: Nullable<AsyncError>;
  data?: Nullable<T>;
}

export interface UseAsyncResponse<T> {
  result: Nullable<T>;
  asyncCallback: (...args: unknown[]) => Promise<Nullable<T>>;
  isLoading: boolean;
  error: Nullable<AsyncError>;
}

const isString = (value: unknown): value is string => typeof value === 'string';

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

const readStringField = (source: unknown, field: string): Nullable<string> => {
  if (!isRecord(source)) {
    return null;
  }

  const value = source[field];

  return isString(value) && value ? value : null;
};

const readNestedResponseField = (
  thrown: unknown,
  field: string,
): Nullable<string> => {
  if (!isRecord(thrown)) {
    return null;
  }

  const { response } = thrown;
  if (!isRecord(response)) {
    return null;
  }

  return readStringField(response.data, field);
};

export class AsyncOperationError implements AsyncError {
  code?: string;
  message: string;

  constructor(json: JsonObject) {
    this.code = isString(json.code) ? json.code : undefined;
    this.message = isString(json.message) ? json.message : '';
  }

  static fromUnknown(
    thrown: unknown,
    fallbackMessage: string,
  ): AsyncOperationError {
    const code =
      readNestedResponseField(thrown, 'code') ??
      readStringField(thrown, 'code') ??
      undefined;

    const message =
      readNestedResponseField(thrown, 'message') ??
      readStringField(thrown, 'message') ??
      (isString(thrown) && thrown ? thrown : null) ??
      fallbackMessage;

    return new AsyncOperationError({ code, message });
  }
}
