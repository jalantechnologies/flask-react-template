# Task Management Feature

## Overview
This feature provides a complete CRUD interface for managing tasks in the frontend application.

## Features
- ✅ **Create Tasks**: Add new tasks with title and description
- ✅ **Read Tasks**: View all tasks with pagination
- ✅ **Update Tasks**: Edit existing tasks
- ✅ **Delete Tasks**: Remove tasks with confirmation
- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Loading States**: Shows loading indicators during API calls
- ✅ **Error Handling**: Displays error messages for failed operations
- ✅ **Success Notifications**: Shows success messages for completed operations

## How to Run

### 1. Start the Backend
```bash
# Activate virtual environment
pipenv shell

# Start the backend server
python src/apps/backend/server.py
```
The backend will run on `http://localhost:8080`

### 2. Start the Frontend
```bash
# Install dependencies (if not already done)
npm install

# Start the frontend development server
npm run serve:frontend
```
The frontend will run on `http://localhost:3000`

### 3. Access the Task Management
1. Open your browser and go to `http://localhost:3000`
2. Login to your account
3. Click on "Tasks" in the sidebar navigation
4. Or directly navigate to `http://localhost:3000/tasks`

## Usage

### Creating a Task
1. Click the "Add Task" button
2. Fill in the title and description
3. Click "Create Task"

### Editing a Task
1. Click the edit icon (pencil) on any task card
2. Modify the title and/or description
3. Click "Update Task"

### Deleting a Task
1. Click the delete icon (trash) on any task card
2. Confirm the deletion in the popup dialog

### Navigation
- Use the pagination controls at the bottom to navigate through multiple pages of tasks
- The interface shows "Showing X of Y tasks" to indicate the current page

## API Endpoints Used

The frontend uses these backend API endpoints:
- `GET /api/accounts/{accountId}/tasks` - Get all tasks (with pagination)
- `POST /api/accounts/{accountId}/tasks` - Create a new task
- `PATCH /api/accounts/{accountId}/tasks/{taskId}` - Update a task
- `DELETE /api/accounts/{accountId}/tasks/{taskId}` - Delete a task

## File Structure

```
src/apps/frontend/
├── components/task/
│   ├── task-form.component.tsx    # Form for creating/editing tasks
│   └── task-card.component.tsx    # Individual task display card
├── pages/tasks/
│   └── index.tsx                  # Main tasks page
├── services/
│   └── task.service.ts            # API service for task operations
└── types/
    └── task.ts                    # TypeScript types for tasks
```

## Technologies Used
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Hot Toast** for notifications
- **Axios** for API calls
- **React Router** for navigation

## Features in Detail

### Task Form Component
- Form validation for required fields
- Loading states during submission
- Error handling and display
- Reusable for both create and edit operations

### Task Card Component
- Displays task title, description, and timestamps
- Edit and delete action buttons
- Responsive design with hover effects
- Loading state for delete operations

### Tasks Page
- Grid layout for task cards
- Pagination controls
- Empty state with call-to-action
- Loading states for initial data fetch
- Error handling for API failures

## Troubleshooting

### Common Issues

1. **Backend not running**: Make sure the Flask backend is running on port 8080
2. **CORS issues**: The backend is configured to allow requests from localhost:3000
3. **Authentication**: Make sure you're logged in to access the tasks page
4. **API errors**: Check the browser console for detailed error messages

### Development Tips

- The frontend automatically refreshes when you make changes to the code
- Check the browser's Network tab to see API requests
- Use the browser's Developer Tools to debug any issues
- The backend logs will show incoming API requests

## Future Enhancements

Potential improvements for the task management feature:
- Task categories/tags
- Task priority levels
- Due dates and reminders
- Task search and filtering
- Bulk operations (delete multiple tasks)
- Task completion status
- Task comments system
