import React, { useState, useEffect } from 'react';
import clsx from 'clsx';

import { Button, FormControl, Input, ParagraphMedium } from 'frontend/components';
import {
  TaskFormData,
  TaskValidationError,
  CreateTaskRequest,
  UpdateTaskRequest,
} from 'frontend/types';
import { ButtonType, ButtonKind } from 'frontend/types/button';

interface TaskFormProps {
  initialData?: TaskFormData;
  onSubmit: (data: TaskFormData) => Promise<void>;
  onCancel?: () => void;
  isSubmitting?: boolean;
  submitButtonText?: string;
  showCancelButton?: boolean;
  title?: string;
  autoFocus?: boolean;
  errors?: TaskValidationError;
}

const TaskForm: React.FC<TaskFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting = false,
  submitButtonText = 'Save Task',
  showCancelButton = false,
  title = 'Task Details',
  autoFocus = false,
  errors: externalErrors,
}) => {
  const [formData, setFormData] = useState<TaskFormData>({
    title: '',
    description: '',
  });
  const [validationErrors, setValidationErrors] = useState<TaskValidationError>({});

  // Initialize form data
  useEffect(() => {
    if (initialData) {
      setFormData({
        title: initialData.title || '',
        description: initialData.description || '',
      });
    }
  }, [initialData]);

  // Clear validation errors when form data changes
  useEffect(() => {
    if (Object.keys(validationErrors).length > 0) {
      setValidationErrors({});
    }
  }, [formData.title, formData.description]);

  const validateForm = (): boolean => {
    const errors: TaskValidationError = {};

    // Title validation
    if (!formData.title.trim()) {
      errors.title = 'Task title is required';
    } else if (formData.title.trim().length > 200) {
      errors.title = 'Task title cannot exceed 200 characters';
    }

    // Description validation
    if (formData.description.trim().length > 2000) {
      errors.description = 'Task description cannot exceed 2000 characters';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await onSubmit(formData);
    } catch (error) {
      // Error is handled by parent component
    }
  };

  const handleInputChange = (field: keyof TaskFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleCancel = () => {
    setFormData(initialData || { title: '', description: '' });
    setValidationErrors({});
    onCancel?.();
  };

  const getErrorMessage = (field: keyof TaskValidationError): string | undefined => {
    return validationErrors[field] || externalErrors?.[field];
  };

  const titleCharacterCount = formData.title.length;
  const descriptionCharacterCount = formData.description.length;
  const isTitleOverLimit = titleCharacterCount > 200;
  const isDescriptionOverLimit = descriptionCharacterCount > 2000;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
      <h2 className="text-xl font-semibold mb-4 sm:mb-6">{title}</h2>

      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
        {/* Title Field */}
        <FormControl
          label="Task Title"
          error={getErrorMessage('title')}
        >
          <Input
            value={formData.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            placeholder="Enter task title..."
            autoFocus={autoFocus}
            disabled={isSubmitting}
            className={clsx(
              getErrorMessage('title') && 'border-red-500 focus:ring-red-500',
              isTitleOverLimit && 'border-red-500 focus:ring-red-500'
            )}
            maxLength={200}
            aria-label="Task title"
            aria-describedby={getErrorMessage('title') ? 'title-error' : 'title-help'}
            aria-required="true"
          />
          <div className="flex justify-between items-center mt-1">
            <span id="title-help" className="text-xs text-gray-500">
              Required
            </span>
            <span className={clsx(
              'text-xs',
              isTitleOverLimit ? 'text-red-500' : 'text-gray-500',
              isTitleOverLimit && 'font-medium'
            )}>
              {titleCharacterCount}/200
            </span>
          </div>
        </FormControl>

        {/* Description Field */}
        <FormControl
          label="Description"
          error={getErrorMessage('description')}
        >
          <textarea
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            placeholder="Enter task description..."
            disabled={isSubmitting}
            className={clsx(
              'w-full min-h-[120px] rounded-lg border border-gray-300 p-3 text-sm',
              'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
              'disabled:bg-gray-100 disabled:cursor-not-allowed',
              'resize-y',
              (getErrorMessage('description') || isDescriptionOverLimit) && 'border-red-500 focus:ring-red-500'
            )}
            maxLength={2000}
            rows={4}
            aria-label="Task description"
            aria-describedby={getErrorMessage('description') ? 'description-error' : 'description-help'}
          />
          <div className="flex justify-between items-center mt-1">
            <span id="description-help" className="text-xs text-gray-500">
              Optional
            </span>
            <span className={clsx(
              'text-xs',
              isDescriptionOverLimit ? 'text-red-500' : 'text-gray-500',
              isDescriptionOverLimit && 'font-medium'
            )}>
              {descriptionCharacterCount}/2000
            </span>
          </div>
        </FormControl>

        {/* General Errors */}
        {externalErrors?.general && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <div className="text-sm text-red-700">
              {externalErrors.general}
            </div>
          </div>
        )}

        {/* Form Actions */}
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          {showCancelButton && (
            <Button
              type={ButtonType.BUTTON}
              kind={ButtonKind.SECONDARY}
              onClick={handleCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          )}

          <Button
            type={ButtonType.SUBMIT}
            kind={ButtonKind.PRIMARY}
            isLoading={isSubmitting}
            disabled={isSubmitting || isTitleOverLimit || isDescriptionOverLimit}
          >
            {isSubmitting ? 'Saving...' : submitButtonText}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default TaskForm;