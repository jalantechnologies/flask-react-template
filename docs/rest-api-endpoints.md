# REST API Endpoints

This document covers all available REST API endpoints, their request/response formats, error codes, and usage examples.

---

## Device Token Endpoints

The Device Token API manages push notification device registrations.

### POST /api/accounts/:accountId/devices

Register a new device token for push notifications.

**Authentication:** Required

**Path Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `accountId` | Yes | The authenticated user's account ID |

**Request Body:**

```json
{
  "device_token": "string (required) - Firebase or APNs token",
  "platform": "string (required) - 'android' or 'ios'",
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
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | DEVICE_TOKEN_ERR_03 | Missing request body |
| 400 | DEVICE_TOKEN_ERR_03 | Missing or empty device_token |
| 400 | DEVICE_TOKEN_ERR_03 | Missing or empty platform |
| 400 | DEVICE_TOKEN_ERR_02 | Invalid platform value |
| 409 | DEVICE_TOKEN_ERR_04 | Device token already registered |
| 401 | ACCESS_TOKEN_ERR_03 | Authorization header is missing |
| 401 | ACCESS_TOKEN_ERR_05 | Invalid access token |

**Example Request:**

```bash
POST /api/accounts/:accountId/devices
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "device_token": "fcm_token_here",
  "platform": "android",
  "device_info": {
    "app_version": "1.0.0",
    "os_version": "14",
    "device_model": "Pixel 8"
  }
}
```

---

### GET /api/accounts/:accountId/devices

Retrieve all active device tokens for the authenticated account, ordered by most recently created.

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
      "last_used_at": "2025-01-15T10:30:00Z"
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
GET /api/accounts/:accountId/devices
Authorization: Bearer <token>
```

---

### PATCH /api/accounts/:accountId/devices/:deviceId

Update a specific device token. Unsupported fields are rejected. Sending an empty PATCH request is allowed and updates last_used_at without modifying any other fields (heartbeat).


**Authentication:** Required

**Path Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `accountId` | Yes | The authenticated user's account ID |
| `deviceId` | Yes | The unique ID of the device token to update |

**Allowed Request Fields:**

| Parameter | Optional | Notes |
|-----------|----------|-------------|
| `device_token` | Yes | Must be non-empty if provided|
| `device_info` | Yes | Must be an object |

**Request Body:**

```json
{
  "device_info": {
    "app_version": "1.1.0",
    "os_version": "15.0"
  },
  "device_token": "updated_fcm_token"
}
```

**Response (200 OK):**

```json
{
  "id": "device_token_id",
  "platform": "android",
  "device_info": {
    "app_version": "1.1.0",
    "os_version": "15.0"
  },
  "active": true,
  "last_used_at": "2025-01-15T10:35:00Z"
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | DEVICE_TOKEN_ERR_03 | Unsupported PATCH fields |
| 400 | DEVICE_TOKEN_ERR_03 | Empty device token |
| 400 | DEVICE_TOKEN_ERR_03 | Device info is not an object |
| 404 | DEVICE_TOKEN_ERR_01 | Device token not found |
| 409 | DEVICE_TOKEN_ERR_04 | Device token already registered |
| 401 | ACCESS_TOKEN_ERR_03 | Authorization header is missing |
| 401 | ACCESS_TOKEN_ERR_05 | Invalid access token |

**Example Request:**

```bash
PATCH /api/accounts/:accountId/devices/:deviceId
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "device_info": {
    "app_version": "1.1.0",
    "os_version": "15.0"
  },
  "device_token": "updated_fcm_token"
}
```

---

### DELETE /api/accounts/:accountId/devices/:deviceId

Deactivate (soft delete) a specific device token. The token record remains in the database but is marked as inactive and will no longer receive push notifications. If deviceId is invalid or does not belong to the account, 404 Device token not found is returned.

**Authentication:** Required

**Path Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `accountId` | Yes | The authenticated user's account ID |
| `deviceId` | Yes | The unique ID of the device token to deactivate |

**Response (204 No Content):**

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 404 | DEVICE_TOKEN_ERR_01 | Device token not found |
| 401 | ACCESS_TOKEN_ERR_01 | Unauthorized access |
| 401 | ACCESS_TOKEN_ERR_03 | Authorization header is missing |

**Example Request:**

```bash
DELETE /api/accounts/account_123/devices/device_token_id_456
Authorization: Bearer <token>
```

---

## Error Response Format

All errors follow a consistent format:

```json
{
  "message": "error_message",
  "code": "ERROR_CODE"
}
```

### Device Token Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| DEVICE_TOKEN_ERR_01 | 404 | Device token not found |
| DEVICE_TOKEN_ERR_02 | 400 | Invalid platform (must be 'android' or 'ios') |
| DEVICE_TOKEN_ERR_03 | 400 | Bad Request |
| DEVICE_TOKEN_ERR_04 | 409 | Device token already registered |

---

## Security Considerations

- **JWT Authentication:** All endpoints require valid JWT authentication tokens
- **Account Ownership:** Users can only manage their own device tokens. Attempts to access or modify another account's devices will result in a 401 unauthorized error

---

## Database Schema

**Collection:** `device_tokens`

**Indexes:**

- Unique index on `device_token` (one token = one device)
- Compound index on `(account_id, active, created_at desc)` for efficient querying
- TTL index on `last_used_at` for automatic hard deletion of inactive tokens after 30 days of inactivity. Once expired, the device token record is permanently removed from the database and must be re-registered by the client.


**Fields:**

| Field | Description |
|-------|-------------|
| `account_id` | String representation of the account ID (e.g., MongoDB ObjectId hex string) |
| `device_token` | FCM or APNs token string |
| `platform` | One of 'android' or 'ios' |
| `device_info` | Optional object containing `app_version`, `os_version`, `device_model` |
| `active` | Boolean flag for soft deletion |
| `last_used_at` | Timestamp of last token usage |
| `created_at`, `updated_at` | Automatic timestamps |

---
