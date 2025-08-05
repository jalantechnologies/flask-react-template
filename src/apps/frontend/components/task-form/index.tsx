import React, { useState, useEffect } from 'react';

import Button from 'frontend/components/button';
import FormControl from 'frontend/components/form-control';
import Input from 'frontend/components/input';
import VerticalStackLayout from 'frontend/components/layouts/vertical-stack-layout';
import { ButtonKind, ButtonType } from 'frontend/types/button';
import {
  CreateTaskRequest,
  Task,
  UpdateTaskRequest,
} from 'frontend/types/task';

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: CreateTaskRequest | UpdateTaskRequest) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const TaskForm: React.FC<TaskFormProps> = ({
  task,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [errors, setErrors] = useState<{
    title?: string;
    description?: string;
  }>({});

  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description);
    }
  }, [task]);

  const validateForm = () => {
    const newErrors: { title?: string; description?: string } = {};

    if (!title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!description.trim()) {
      newErrors.description = 'Description is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      const formData = {
        title: title.trim(),
        description: description.trim(),
      };

      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <VerticalStackLayout gap={4}>
        <FormControl label="Title" error={errors.title}>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter task title"
            testId="task-title-input"
          />
        </FormControl>

        <FormControl label="Description" error={errors.description}>
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter task description"
            testId="task-description-input"
          />
        </FormControl>

        <div className="flex gap-3">
          <Button
            type={ButtonType.SUBMIT}
            kind={ButtonKind.PRIMARY}
            isLoading={isLoading}
            disabled={isLoading}
          >
            {task ? 'Update Task' : 'Create Task'}
          </Button>
          <Button
            type={ButtonType.BUTTON}
            kind={ButtonKind.SECONDARY}
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
        </div>
      </VerticalStackLayout>
    </form>
  );
};

export default TaskForm;
