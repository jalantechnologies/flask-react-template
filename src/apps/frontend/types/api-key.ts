import { JsonObject, Nullable } from 'frontend/types/common-types';

export enum ApiKeyStatus {
  ACTIVE = 'active',
  REVOKED = 'revoked',
  EXPIRED = 'expired',
}

export class ApiKey {
  id: string;
  accountId: string;
  name: string;
  status: ApiKeyStatus;
  createdAt: Nullable<string>;
  expiresAt: Nullable<string>;
  lastUsedAt: Nullable<string>;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.accountId = json.account_id as string;
    this.name = json.name as string;
    this.status = json.status as ApiKeyStatus;
    this.createdAt = (json.created_at as Nullable<string>) ?? null;
    this.expiresAt = (json.expires_at as Nullable<string>) ?? null;
    this.lastUsedAt = (json.last_used_at as Nullable<string>) ?? null;
  }
}

export class CreatedApiKey {
  // The plaintext secret is present only on the create response and is shown once.
  apiKey: ApiKey;
  plaintextKey: string;

  constructor(json: JsonObject) {
    this.apiKey = new ApiKey(json);
    this.plaintextKey = json.key as string;
  }
}
