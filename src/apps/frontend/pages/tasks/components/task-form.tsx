import React, { useState } from 'react';
import { 
  Button, 
  FormControl, 
  Input, 
  VerticalStackLayout,
  H2 
} from 'frontend/components';
import { ButtonKind, ButtonType } from 'frontend/types/button';
import { AsyncError } from 'frontend/types';

interface Task {
  id: string;
  title: string;
  description: string;
  account_id: string;
}

interface TaskFormProps {
  task?: Task | null;
  onSubmit: (taskData: { title: string; description: string }) => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
}

const TaskForm: React.FC<TaskFormProps> = ({ task, onSubmit, onCancel, isLoading }) => {
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [errors, setErrors] = useState<{ title?: string; description?: string }>({});

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      await onSubmit({ title: title.trim(), description: description.trim() });
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <div className="rounded-sm border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-boxdark">
      <H2>{task ? 'Edit Task' : 'Create New Task'}</H2>
      
      <form onSubmit={handleSubmit}>
        <VerticalStackLayout gap={5}>
          <FormControl label="Title" error={errors.title}>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter task title"
              error={errors.title}
              disabled={isLoading}
            />
          </FormControl>
          
          <FormControl label="Description" error={errors.description}>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter task description"
              error={errors.description}
              disabled={isLoading}
            />
          </FormControl>
          
          <div className="flex gap-4">
            <Button
              type={ButtonType.SUBMIT}
              kind={ButtonKind.PRIMARY}
              isLoading={isLoading}
            >
              {task ? 'Update Task' : 'Create Task'}
            </Button>
            
            <Button
              type={ButtonType.BUTTON}
              kind={ButtonKind.TERTIARY}
              onClick={onCancel}
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </VerticalStackLayout>
      </form>
    </div>
  );
};

export default TaskForm;
