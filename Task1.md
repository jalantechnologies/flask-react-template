## Description
This pull request implements the backend API functionality for managing comments in a task management system as per the assessment requirements. The implementation includes Flask-based RESTful endpoints supporting full CRUD (Create, Read, Update, Delete) operations on comments associated with specific tasks and accounts. Additionally, comprehensive automated test coverage is added to verify both service-level and API-level behavior, including authorization, input validation, and data isolation.

### Endpoints Implemented
- `POST /api/accounts/{account_id}/tasks/{task_id}/comments`: Create a new comment  
- `GET /api/accounts/{account_id}/tasks/{task_id}/comments`: Retrieve all comments for a task  
- `PUT /api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}`: Update a comment’s text  
- `DELETE /api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}`: Delete a comment  


## Database schema changes
No schema modification beyond existing `Comment` and `Account` collections. Used standard fields:
- `id`, `account_id`, `task_id`, `text`, `created_at`, `updated_at`.

## Tests
### Automated test cases added
- Verified successful creation, update, retrieval, and deletion of comments through APIs.
- Validated input fields (missing, empty, or whitespace-only text scenarios).
- Tested authentication failures (missing header, invalid tokens, cross-account access).
- Confirmed isolation of comments between different accounts and tasks.

### Manual test cases run
- Created comment via `/comments` endpoint and confirmed database persistence. 
- Updated comment text and verified `updated_at` timestamp changed.  
- Sent malformed JSON body—received 400 Bad Request with appropriate error message.  
- Retrieved and deleted comments, ensuring the list updated accordingly.
