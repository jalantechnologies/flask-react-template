import APIService from 'frontend/services/api.service';
import {
  AccessToken,
  ApiKey,
  ApiResponse,
  CreatedApiKey,
} from 'frontend/types';
import { JsonObject, Nullable } from 'frontend/types/common-types';

interface CreateApiKeyPayload {
  name: string;
  expiresInDays?: Nullable<number>;
}

const authHeader = (accessToken: AccessToken) => ({
  headers: { Authorization: `Bearer ${accessToken.token}` },
});

export default class ApiKeyService extends APIService {
  listApiKeys = async (
    accessToken: AccessToken,
  ): Promise<ApiResponse<ApiKey[]>> => {
    const response = await this.apiClient.get<{ items: JsonObject[] }>(
      `/accounts/${accessToken.accountId}/api-keys`,
      authHeader(accessToken),
    );
    return new ApiResponse(response.data.items.map((item) => new ApiKey(item)));
  };

  createApiKey = async (
    accessToken: AccessToken,
    payload: CreateApiKeyPayload,
  ): Promise<ApiResponse<CreatedApiKey>> => {
    const body: JsonObject = { name: payload.name };
    if (payload.expiresInDays != null) {
      body.expires_in_days = payload.expiresInDays;
    }
    const response = await this.apiClient.post<JsonObject>(
      `/accounts/${accessToken.accountId}/api-keys`,
      body,
      authHeader(accessToken),
    );
    return new ApiResponse(new CreatedApiKey(response.data));
  };

  revokeApiKey = async (
    accessToken: AccessToken,
    apiKeyId: string,
  ): Promise<ApiResponse<void>> =>
    this.apiClient.delete(
      `/accounts/${accessToken.accountId}/api-keys/${apiKeyId}`,
      authHeader(accessToken),
    );
}
