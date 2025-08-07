# Comment API Documentation

This document describes the Comment API functionality for managing comments on tasks.

## Overview

The Comment API provides CRUD operations for managing comments associated with tasks. Comments are tied to specific tasks and accounts, ensuring proper data isolation and security.

## API Endpoints

### Base URL
```
/api/accounts/{account_id}/tasks/{task_id}/comments
```

### 1. Create Comment

**POST** `/api/accounts/{account_id}/tasks/{task_id}/comments`

Creates a new comment for a specific task.

**Request Body:**
```json
{
  "content": "This is a comment content"
}
```

**Response (201 Created):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "task_id": "507f1f77bcf86cd799439012",
  "account_id": "507f1f77bcf86cd799439013",
  "content": "This is a comment content",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### 2. Get Comment

**GET** `/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}`

Retrieves a specific comment by ID.

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "task_id": "507f1f77bcf86cd799439012",
  "account_id": "507f1f77bcf86cd799439013",
  "content": "This is a comment content",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### 3. Get Paginated Comments

**GET** `/api/accounts/{account_id}/tasks/{task_id}/comments?page=1&size=10`

Retrieves paginated comments for a specific task.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `size` (optional): Number of items per page (default: 10)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "507f1f77bcf86cd799439011",
      "task_id": "507f1f77bcf86cd799439012",
      "account_id": "507f1f77bcf86cd799439013",
      "content": "This is a comment content",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "pagination_params": {
    "page": 1,
    "size": 10,
    "offset": 0
  },
  "total_count": 1
}
```

### 4. Update Comment

**PATCH** `/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}`

Updates an existing comment.

**Request Body:**
```json
{
  "content": "Updated comment content"
}
```

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "task_id": "507f1f77bcf86cd799439012",
  "account_id": "507f1f77bcf86cd799439013",
  "content": "Updated comment content",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:30:00Z"
}
```

### 5. Delete Comment

**DELETE** `/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}`

Deletes a comment (soft delete).

**Response (204 No Content):**
No response body.

## Error Responses

### 400 Bad Request
```json
{
  "code": "COMMENT_ERR_02",
  "message": "Content is required"
}
```

### 401 Unauthorized
```json
{
  "code": "AUTH_ERR_01",
  "message": "Invalid or missing access token"
}
```

### 404 Not Found
```json
{
  "code": "TASK_ERR_01",
  "message": "Task with id 507f1f77bcf86cd799439011 not found."
}
```

```json
{
  "code": "COMMENT_ERR_01",
  "message": "Comment with id 507f1f77bcf86cd799439011 not found."
}
```

## Authentication

All endpoints require authentication using Bearer tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## Data Model

### Comment
```typescript
interface Comment {
  id: string;
  task_id: string;
  account_id: string;
  content: string;
  created_at: string;
  updated_at: string;
}
```

## Business Rules

1. **Task Ownership**: Comments can only be created for tasks that belong to the authenticated user's account.
2. **Content Validation**: Comment content is required and cannot be empty.
3. **Soft Delete**: Comments are soft-deleted (marked as inactive) rather than permanently removed.
4. **Pagination**: Comments are returned in descending order by creation date (newest first).
5. **Data Isolation**: Users can only access comments for tasks in their own account.

## Testing

Comprehensive automated tests are included in:
- `tests/modules/task/test_comment_api.py` - API endpoint tests
- `tests/modules/task/test_comment_service.py` - Service layer tests
- `tests/modules/task/base_test_comment.py` - Base test class for comments

Run tests with:
```bash
cd flask-react-template
python -m pytest tests/modules/task/test_comment_api.py -v
python -m pytest tests/modules/task/test_comment_service.py -v
``` 