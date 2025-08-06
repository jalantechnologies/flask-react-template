import React, { useState, useEffect } from 'react';
import { Button, Input, VerticalStackLayout } from 'frontend/components';
import { ButtonKind, ButtonType } from 'frontend/types/button';

interface TaskFormProps {
  onSubmit: (data: { title: string; description: string }) => void;
  onCancel: () => void;
  title: string;
  initialData?: {
    title: string;
    description: string;
  };
}

const TaskForm: React.FC<TaskFormProps> = ({
  onSubmit,
  onCancel,
  title,
  initialData,
}) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
  });
  const [errors, setErrors] = useState<{
    title?: string;
    description?: string;
  }>({});

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const validateForm = () => {
    const newErrors: { title?: string; description?: string } = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleInputChange = (field: 'title' | 'description', value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>

      <form onSubmit={handleSubmit}>
        <VerticalStackLayout gap={2}>
          <div>
            <label
              htmlFor="title"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Title
            </label>
            <Input
              id="title"
              type="text"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              placeholder="Enter task title"
              error={errors.title}
            />
          </div>

          <div>
            <label
              htmlFor="description"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Description
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Enter task description"
              rows={4}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.description ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description}</p>
            )}
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type={ButtonType.BUTTON}
              onClick={onCancel}
              kind={ButtonKind.SECONDARY}
            >
              Cancel
            </Button>
            <Button type={ButtonType.SUBMIT} kind={ButtonKind.PRIMARY}>
              {initialData ? 'Update' : 'Create'}
            </Button>
          </div>
        </VerticalStackLayout>
      </form>
    </div>
  );
};

export default TaskForm;
