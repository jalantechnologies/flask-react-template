// filepath: /Users/pushkalgoyal/project/flask-react-template/src/apps/frontend/pages/FormValues/FormValues.page.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import TaskService from 'frontend/services/task.service';
import { ApiResponse } from 'frontend/types';

// interface Task {
//   id: string;
//   title: string;
//   description: string;
//   priority: 'low' | 'medium' | 'high';
//   dueDate?: string;
//   status: 'pending' | 'in-progress' | 'completed';
//   createdAt: string;
// }

interface TaskFormData {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  dueDate: string;
}

export const FormValues: React.FC = () => {
  const navigate = useNavigate();
  const [taskInfo, setTaskInfo] = useState<TaskFormData>({
    title: '',
    description: '',
    priority: 'medium',
    dueDate: '',
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const tc = new TaskService();

  const updateFormField = (
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const fieldName = event.target.name;
    const fieldValue = event.target.value;

    setTaskInfo((currentData) => ({
      ...currentData,
      [fieldName]: fieldValue,
    }));
  };
  const createTasksfn = async (
    title: string,
    description: string,
  ): Promise<ApiResponse<void>> => {
    console.log(title, description);
    return tc.createTasks(title, description);
  };
  // const processFormSubmission = async (event: React.FormEvent) => {
  //   event.preventDefault();
  //   setIsProcessing(true);

  //   try {
  //     console.log('Task information submitted:', taskInfo);

  //     // Simulate API call with setTimeout
  //     await new Promise((resolve) => setTimeout(resolve, 1000));

  //     // Here you would typically call your API
  //     // await fetch('/api/tasks', { method: 'POST', body: JSON.stringify(taskInfo) });

  //     alert(`Task "${taskInfo.title}" has been created successfully!`);
  //     navigate('/dashboard');
  //   } catch (error) {
  //     console.error('Submission failed:', error);
  //     alert('Failed to create task. Please try again.');
  //   } finally {
  //     setIsProcessing(false);
  //   }
  // };

  const cancelFormEntry = () => {
    const confirmCancel = window.confirm(
      'Are you sure you want to cancel? Your changes will be lost.',
    );
    if (confirmCancel) {
      navigate('/dashboard');
    }
  };
  const handleCreateTask = async () => {
    if (!taskInfo.title || !taskInfo.description) {
      alert('Please fill in both title and description');
      return;
    }

    setIsProcessing(true);
    try {
      await createTasksfn(taskInfo.title, taskInfo.description);
      alert(`Task "${taskInfo.title}" created successfully!`);
      navigate('/tasks');
    } catch (error) {
      console.error('Error creating task:', error);
      alert('Failed to create task');
    } finally {
      setIsProcessing(false);
    }
  };
  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    // eslint-disable-next-line no-void
    void handleCreateTask(); // Fire and forget - don't await
  };

  return (
    <div className="task-creation-wrapper">
      <div className="form-header">
        <h1>Add New Task</h1>
        <p>Fill out the details below to create a new task</p>
      </div>

      <form onSubmit={handleSubmit} className="task-entry-form">
        <div className="input-section">
          <label htmlFor="title" className="field-label">
            Task Name *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={taskInfo.title}
            onChange={updateFormField}
            placeholder="What needs to be done?"
            className="text-input"
            required
            minLength={3}
          />
        </div>

        <div className="input-section">
          <label htmlFor="description" className="field-label">
            Task Details *
          </label>
          <textarea
            id="description"
            name="description"
            value={taskInfo.description}
            onChange={updateFormField}
            placeholder="Describe the task in detail..."
            className="text-area"
            required
            minLength={1}
          />
        </div>

        <div className="button-section">
          <button
            type="button"
            onClick={cancelFormEntry}
            className="cancel-button"
            disabled={isProcessing}
          >
            Cancel Entry
          </button>
          <button
            type="submit"
            className="submit-button"
            disabled={isProcessing || !taskInfo.title || !taskInfo.description}
            // eslint-disable-next-line @typescript-eslint/no-misused-promises
            onClick={handleCreateTask}
          >
            {isProcessing ? 'Creating Task...' : 'Create Task'}
          </button>
        </div>
      </form>

      <style>{`
        .task-creation-wrapper {
          max-width: 600px;
          margin: 2rem auto;
          padding: 2rem;
          background: #ffffff;
          border-radius: 10px;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        }

        .form-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .form-header h1 {
          color: #2c3e50;
          font-size: 2rem;
          margin-bottom: 0.5rem;
        }

        .form-header p {
          color: #7f8c8d;
          font-size: 1.1rem;
        }

        .task-entry-form {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .input-section {
          display: flex;
          flex-direction: column;
        }

        .field-label {
          font-weight: 600;
          color: #34495e;
          margin-bottom: 0.5rem;
          font-size: 0.95rem;
        }

        .text-input,
        .text-area,
        .selection-input,
        .date-input {
          padding: 0.75rem;
          border: 2px solid #ecf0f1;
          border-radius: 6px;
          font-size: 1rem;
          transition: border-color 0.2s ease;
          font-family: inherit;
        }

        .text-input:focus,
        .text-area:focus,
        .selection-input:focus,
        .date-input:focus {
          outline: none;
          border-color: #3498db;
        }

        .text-area {
          resize: vertical;
          font-family: inherit;
        }

        .button-section {
          display: flex;
          gap: 1rem;
          margin-top: 1rem;
        }

        .cancel-button,
        .submit-button {
          flex: 1;
          padding: 0.875rem;
          border: none;
          border-radius: 6px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .cancel-button {
          background-color: #95a5a6;
          color: white;
        }

        .cancel-button:hover:not(:disabled) {
          background-color: #7f8c8d;
        }

        .submit-button {
          background-color: #3498db;
          color: white;
        }

        .submit-button:hover:not(:disabled) {
          background-color: #2980b9;
        }

        .submit-button:disabled,
        .cancel-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        @media (max-width: 640px) {
          .task-creation-wrapper {
            margin: 1rem;
            padding: 1.5rem;
          }

          .button-section {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default FormValues;
