import { JsonObject, Nullable } from 'frontend/types/common-types';

export interface AsyncError {
  code: string;
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

export class AsyncOperationError implements AsyncError {
  code: string;
  message: string;

  constructor(json: JsonObject) {
    this.code = json.code as string;
    this.message = json.message as string;
  }
}
