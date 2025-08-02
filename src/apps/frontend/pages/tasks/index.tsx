import React, { useState, useEffect, useCallback } from 'react';

import { useAccountContext } from 'frontend/contexts/account.provider';
import {
  taskService,
  Task,
  Comment,
  CreateTaskRequest,
  CreateCommentRequest,
} from 'frontend/services/task.service';

import './tasks.css';

interface TaskWithComments extends Task {
  comments: Comment[];
}

const Tasks = () => {
  const { accountDetails } = useAccountContext();
  const [tasks, setTasks] = useState<TaskWithComments[]>([]);
  const [newTaskText, setNewTaskText] = useState('');
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [editingText, setEditingText] = useState('');
  const [showComments, setShowComments] = useState<string | null>(null);
  const [newCommentText, setNewCommentText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTasks = useCallback(async () => {
    if (!accountDetails?.id) return;

    try {
      setLoading(true);
      setError(null);
      const response = await taskService.getTasks(accountDetails.id);

      const tasksWithComments = await Promise.all(
        response.items.map(async (task) => {
          try {
            const commentsResponse = await taskService.getComments(
              accountDetails.id,
              task.id,
            );
            return {
              ...task,
              comments: commentsResponse.items,
            };
          } catch (err) {
            // eslint-disable-next-line no-console
            console.error(`Failed to load comments for task ${task.id}:`, err);
            return {
              ...task,
              comments: [],
            };
          }
        }),
      );

      setTasks(tasksWithComments);
    } catch (err) {
      if (err.message === 'Access token not found') {
        setError('Authentication required. Please log in again.');
      } else {
        setError('Failed to load tasks');
      }
      // eslint-disable-next-line no-console
      console.error('Error loading tasks:', err);
    } finally {
      setLoading(false);
    }
  }, [accountDetails?.id]);

  useEffect(() => {
    if (accountDetails?.id) {
      loadTasks().catch(() => {});
    }
  }, [loadTasks]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!accountDetails?.id || !newTaskText.trim()) return;

    const submitTask = async () => {
      try {
        setLoading(true);
        setError(null);

        const taskData: CreateTaskRequest = {
          title: newTaskText.trim(),
          description: newTaskText.trim(),
        };

        const newTask = await taskService.createTask(
          accountDetails.id,
          taskData,
        );
        const taskWithComments: TaskWithComments = {
          ...newTask,
          comments: [],
        };
        setTasks([taskWithComments, ...tasks]);
        setNewTaskText('');
      } catch (err) {
        if (err instanceof Error && err.message === 'Access token not found') {
          setError('Authentication required. Please log in again.');
        } else {
          setError('Failed to create task');
        }
        // eslint-disable-next-line no-console
        console.error('Error creating task:', err);
      } finally {
        setLoading(false);
      }
    };

    submitTask().catch(() => {});
  };

  const handleEdit = (task: TaskWithComments) => {
    setEditingTaskId(task.id);
    setEditingText(task.title);
  };

  const handleSave = async (taskId: string) => {
    if (!accountDetails?.id || !editingText.trim()) return;

    try {
      setLoading(true);
      setError(null);

      const taskData = {
        title: editingText.trim(),
        description: editingText.trim(),
      };

      const updatedTask = await taskService.updateTask(
        accountDetails.id,
        taskId,
        taskData,
      );
      setTasks(
        tasks.map((task) =>
          task.id === taskId ? { ...task, ...updatedTask } : task,
        ),
      );
      setEditingTaskId(null);
      setEditingText('');
    } catch (err) {
      if (err instanceof Error && err.message === 'Access token not found') {
        setError('Authentication required. Please log in again.');
      } else {
        setError('Failed to update task');
      }
      // eslint-disable-next-line no-console
      console.error('Error updating task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEditingTaskId(null);
    setEditingText('');
  };

  const handleDelete = async (taskId: string) => {
    if (!accountDetails?.id) return;

    try {
      setLoading(true);
      setError(null);

      await taskService.deleteTask(accountDetails.id, taskId);
      setTasks(tasks.filter((task) => task.id !== taskId));
    } catch (err) {
      if (err instanceof Error && err.message === 'Access token not found') {
        setError('Authentication required. Please log in again.');
      } else {
        setError('Failed to delete task');
      }
      // eslint-disable-next-line no-console
      console.error('Error deleting task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (taskId: string) => {
    if (!accountDetails?.id || !newCommentText.trim()) return;

    try {
      setLoading(true);
      setError(null);

      const commentData: CreateCommentRequest = {
        content: newCommentText.trim(),
      };

      const newComment = await taskService.createComment(
        accountDetails.id,
        taskId,
        commentData,
      );
      setTasks(
        tasks.map((task) =>
          task.id === taskId
            ? { ...task, comments: [...task.comments, newComment] }
            : task,
        ),
      );
      setNewCommentText('');
    } catch (err) {
      if (err instanceof Error && err.message === 'Access token not found') {
        setError('Authentication required. Please log in again.');
      } else {
        setError('Failed to add comment');
      }
      // eslint-disable-next-line no-console
      console.error('Error adding comment:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteComment = async (taskId: string, commentId: string) => {
    if (!accountDetails?.id) return;

    try {
      setLoading(true);
      setError(null);

      await taskService.deleteComment(accountDetails.id, taskId, commentId);
      setTasks(
        tasks.map((task) =>
          task.id === taskId
            ? {
                ...task,
                comments: task.comments.filter(
                  (comment) => comment.id !== commentId,
                ),
              }
            : task,
        ),
      );
    } catch (err) {
      if (err instanceof Error && err.message === 'Access token not found') {
        setError('Authentication required. Please log in again.');
      } else {
        setError('Failed to delete comment');
      }
      // eslint-disable-next-line no-console
      console.error('Error deleting comment:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleComments = (taskId: string) => {
    setShowComments(showComments === taskId ? null : taskId);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleSaveClick = (taskId: string) => {
    handleSave(taskId).catch(() => {});
  };

  const handleDeleteClick = (taskId: string) => {
    handleDelete(taskId).catch(() => {});
  };

  const handleAddCommentClick = (taskId: string) => {
    handleAddComment(taskId).catch(() => {});
  };

  const handleDeleteCommentClick = (taskId: string, commentId: string) => {
    handleDeleteComment(taskId, commentId).catch(() => {});
  };

  if (loading && tasks.length === 0) {
    return (
      <div className="tasks-container">
        <div className="loading-state">Loading tasks...</div>
      </div>
    );
  }

  return (
    <div className="tasks-container">
      {/* Error Display */}
      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)} className="error-close">
            ×
          </button>
        </div>
      )}

      {/* Create Task Form */}
      <div className="form-section">
        <h2 className="form-title">Create New Task</h2>
        <form onSubmit={handleSubmit} className="form-row">
          <div className="input-wrapper">
            <input
              type="text"
              value={newTaskText}
              onChange={(e) => setNewTaskText(e.target.value)}
              placeholder="Enter task description..."
              className="task-input"
              required
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            className="submit-button"
            disabled={!newTaskText.trim() || loading}
          >
            {loading ? 'Adding...' : 'Add Task'}
          </button>
        </form>
      </div>

      {/* Tasks Table */}
      <div className="table-section">
        <h2 className="table-title">Tasks</h2>
        {tasks.length === 0 ? (
          <div className="empty-state">
            No tasks created yet. Add your first task above!
          </div>
        ) : (
          <table className="tasks-table">
            <thead>
              <tr>
                <th>Task</th>
                <th>Created</th>
                <th>Comments</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <React.Fragment key={task.id}>
                  <tr>
                    <td>
                      {editingTaskId === task.id ? (
                        <div className="edit-form">
                          <input
                            type="text"
                            value={editingText}
                            onChange={(e) => setEditingText(e.target.value)}
                            className="task-input"
                            disabled={loading}
                          />
                          <button
                            onClick={() => handleSaveClick(task.id)}
                            className="save-button"
                            disabled={!editingText.trim() || loading}
                          >
                            {loading ? 'Saving...' : 'Save'}
                          </button>
                          <button
                            onClick={handleCancel}
                            className="cancel-button"
                            disabled={loading}
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <span className="task-text">{task.title}</span>
                      )}
                    </td>
                    <td>
                      {formatDate(task.created_at || new Date().toISOString())}
                    </td>
                    <td>
                      <div className="comments-info">
                        <span className="comment-count">
                          {task.comments.length} comments
                        </span>
                        <button
                          onClick={() => toggleComments(task.id)}
                          className="view-comments-button"
                          disabled={loading}
                        >
                          {showComments === task.id ? 'Hide' : 'View'} Comments
                        </button>
                      </div>
                    </td>
                    <td>
                      {editingTaskId !== task.id && (
                        <div className="task-actions">
                          <button
                            onClick={() => handleEdit(task)}
                            className="edit-button"
                            disabled={loading}
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteClick(task.id)}
                            className="delete-button"
                            disabled={loading}
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                  {showComments === task.id && (
                    <tr className="comments-row">
                      <td colSpan={4}>
                        <div className="comments-section">
                          <div className="add-comment-form">
                            <input
                              type="text"
                              value={newCommentText}
                              onChange={(e) =>
                                setNewCommentText(e.target.value)
                              }
                              placeholder="Add a comment..."
                              className="comment-input"
                              disabled={loading}
                            />
                            <button
                              onClick={() => handleAddCommentClick(task.id)}
                              className="add-comment-button"
                              disabled={!newCommentText.trim() || loading}
                            >
                              {loading ? 'Adding...' : 'Add Comment'}
                            </button>
                          </div>
                          <div className="comments-list">
                            {task.comments.length === 0 ? (
                              <div className="no-comments">
                                No comments yet. Be the first to comment!
                              </div>
                            ) : (
                              task.comments.map((comment) => (
                                <div key={comment.id} className="comment-item">
                                  <div className="comment-content">
                                    <p className="comment-text">
                                      {comment.content}
                                    </p>
                                    <span className="comment-date">
                                      {formatDate(comment.created_at)}
                                    </span>
                                  </div>
                                  <button
                                    onClick={() =>
                                      handleDeleteCommentClick(
                                        task.id,
                                        comment.id,
                                      )
                                    }
                                    className="delete-comment-button"
                                  >
                                    ×
                                  </button>
                                </div>
                              ))
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Tasks;
