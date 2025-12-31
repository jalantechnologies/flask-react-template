# REST API Endpoints

This document covers all available REST API endpoints, their request/response formats, error codes, and usage examples.

---

## Device Token Endpoints

The Device Token API manages push notification device registrations.

### POST /api/accounts/:accountId/devices

Register or update a device token for push notifications. If a device token already exists, this endpoint will update the existing record (upsert behavior).

**Authentication:** Required

**Path Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `accountId` | Yes | The authenticated user's account ID |

**Request Body:**

```json
{
  "device_token": "string (required) - Firebase or APNs token",
  "platform": "string (required) - 'android', 'ios', or 'web'",
  "device_info": {
    "app_version": "string (optional) - e.g., '1.0.0'",
    "os_version": "string (optional) - e.g., '14.0'",
    "device_model": "string (optional) - e.g., 'iPhone14'"
  }
}
```

**Response (201 Created):**

```json
{
  "id": "device_token_id",
  "device_token": "firebase_or_apns_token",
  "platform": "android",
  "device_info": {
    "app_version": "1.0.0",
    "os_version": "14.0",
    "device_model": "iPhone14"
  },
  "active": true,
  "created_at": "2025-01-15T10:30:00Z",
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | DEVICE_TOKEN_ERR_03 | Missing request body |
| 400 | DEVICE_TOKEN_ERR_03 | Missing or empty device_token |
| 400 | DEVICE_TOKEN_ERR_03 | Missing or empty platform |
| 400 | DEVICE_TOKEN_ERR_02 | Invalid platform value |
| 401 | ACCESS_TOKEN_ERR_03 | Authorization header is missing |
| 401 | ACCESS_TOKEN_ERR_05 | Invalid access token |

**Example Request:**

```bash
curl -X POST https://api.example.com/api/accounts/account_123/devices \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_token": "firebase_token_xyz123",
    "platform": "android",
    "device_info": {
      "app_version": "1.0.0",
      "os_version": "14.0",
      "device_model": "Pixel 8"
    }
  }'
```

**Kotlin (Android) Example:**

```kotlin
suspend fun registerDeviceToken(accountId: String, token: String) {
    val request = RegisterDeviceRequest(
        deviceToken = token,
        platform = "android",
        deviceInfo = DeviceInfo(
            appVersion = BuildConfig.VERSION_NAME,
            osVersion = Build.VERSION.RELEASE,
            deviceModel = Build.MODEL
        )
    )
    api.registerDevice(accountId, request)
}
```

**Swift (iOS) Example:**

```swift
func registerDeviceToken(accountId: String, token: String) async throws {
    let request = RegisterDeviceRequest(
        deviceToken: token,
        platform: "ios",
        deviceInfo: DeviceInfo(
            appVersion: Bundle.main.appVersion,
            osVersion: UIDevice.current.systemVersion,
            deviceModel: UIDevice.current.model
        )
    )
    try await api.registerDevice(accountId: accountId, request: request)
}
```

---

### GET /api/accounts/:accountId/devices

Retrieve all active device tokens for the authenticated account.

**Authentication:** Required

**Path Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `accountId` | Yes | The authenticated user's account ID |

**Response (200 OK):**

```json
{
  "devices": [
    {
      "id": "device_token_id_1",
      "platform": "android",
      "device_info": {
        "app_version": "1.0.0",
        "os_version": "14.0",
        "device_model": "Pixel6"
      },
      "active": true,
      "last_used_at": "2025-01-15T10:30:00Z",
    },
  ]
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 401 | ACCESS_TOKEN_ERR_03 | Authorization header is missing |
| 401 | ACCESS_TOKEN_ERR_05 | Invalid access token |

**Example Request:**

```bash
curl -X GET https://api.example.com/api/accounts/account_123/devices \
  -H "Authorization: Bearer <token>"
```

---

### DELETE /api/accounts/:accountId/devices/:deviceTokenId

Deactivate (soft delete) a specific device token. The token record remains in the database but is marked as inactive and will no longer receive push notifications.

**Authentication:** Required

**Path Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `accountId` | Yes | The authenticated user's account ID |
| `deviceTokenId` | Yes | The unique ID of the device token to deactivate |

**Response (200 OK):**

```json
{
  "message": "Device unregistered successfully"
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 404 | DEVICE_TOKEN_ERR_01 | Device token not found |
| 401 | ACCESS_TOKEN_ERR_01 | Unauthorized access |
| 401 | ACCESS_TOKEN_ERR_03 | Authorization header is missing |
| 401 | ACCESS_TOKEN_ERR_05 | Invalid access token |

**Example Request:**

```bash
curl -X DELETE https://api.example.com/api/accounts/account_123/devices/device_token_id_456 \
  -H "Authorization: Bearer <token>"
```

---

## Error Response Format

All errors follow a consistent format:

```json
{
  "error": "error_message",
  "code": "ERROR_CODE"
}
```

### Device Token Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| DEVICE_TOKEN_ERR_01 | 404 | Device token not found |
| DEVICE_TOKEN_ERR_02 | 400 | Invalid platform (must be 'android', 'ios', or 'web') |
| DEVICE_TOKEN_ERR_03 | 400 | Bad Request |

---

## Security Considerations

- **JWT Authentication:** All endpoints require valid JWT authentication tokens
- **Account Ownership:** Users can only manage their own device tokens. Attempts to access or modify another account's devices will result in a 401 unauthorized error

---

## Database Schema

**Collection:** `device_tokens`

**Indexes:**

- Unique index on `device_token` (one token = one device)
- Compound index on `(account_id, active)` for efficient querying
- Optional TTL index on `last_used_at` for auto-cleanup of stale tokens

**Fields:**

| Field | Description |
|-------|-------------|
| `account_id` | ObjectId reference to the account |
| `device_token` | FCM or APNs token string |
| `platform` | One of 'android', 'ios', or 'web' |
| `device_info` | Optional object containing `app_version`, `os_version`, `device_model` |
| `active` | Boolean flag for soft deletion |
| `last_used_at` | Timestamp of last token usage |
| `created_at`, `updated_at` | Automatic timestamps |

---

## Notes

- **Upsert Behavior:** Registering a device token that already exists will update the existing record rather than creating a duplicate
- **Soft Deletion:** Deleted tokens are marked as inactive rather than physically removed from the database
