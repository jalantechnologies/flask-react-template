import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskForm from '../task-form.component';

// Mock the required components
jest.mock('frontend/components', () => ({
  Button: ({ children, onClick, disabled, isLoading, type, kind }: any) => (
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      data-type={type}
      data-kind={kind}
      data-testid="button"
    >
      {isLoading ? 'Loading...' : children}
    </button>
  ),
  FormControl: ({ children, label, error }: any) => (
    <div data-testid="form-control">
      <label>{label}</label>
      {children}
      {error && <span data-testid="error">{error}</span>}
    </div>
  ),
  Input: ({ value, onChange, disabled, placeholder, maxLength, autoFocus }: any) => (
    <input
      value={value}
      onChange={onChange}
      disabled={disabled}
      placeholder={placeholder}
      maxLength={maxLength}
      autoFocus={autoFocus}
      data-testid="input"
    />
  ),
}));

jest.mock('frontend/components/typography', () => ({
  ParagraphMedium: ({ children }: any) => <p>{children}</p>,
}));

describe('TaskForm', () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders form with required elements', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByDisplayValue('Save Task')).toBeInTheDocument();
    expect(screen.getByLabelText('Task Title')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
    expect(screen.getByText('Required')).toBeInTheDocument();
    expect(screen.getByText('Optional')).toBeInTheDocument();
  });

  it('displays initial data when provided', () => {
    const initialData = {
      title: 'Test Task',
      description: 'Test Description',
    };

    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        initialData={initialData}
      />
    );

    expect(screen.getByDisplayValue('Test Task')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test Description')).toBeInTheDocument();
  });

  it('validates required title field', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByDisplayValue('Save Task');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Task title is required')).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('validates title length limit', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText('Task Title');
    const longTitle = 'x'.repeat(201);

    fireEvent.change(titleInput, { target: { value: longTitle } });

    const submitButton = screen.getByDisplayValue('Save Task');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Task title cannot exceed 200 characters')).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('validates description length limit', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const descriptionInput = screen.getByLabelText('Description');
    const longDescription = 'x'.repeat(2001);

    fireEvent.change(descriptionInput, { target: { value: longDescription } });

    const submitButton = screen.getByDisplayValue('Save Task');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Task description cannot exceed 2000 characters')).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('calls onSubmit with valid data', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText('Task Title');
    const descriptionInput = screen.getByLabelText('Description');
    const submitButton = screen.getByDisplayValue('Save Task');

    fireEvent.change(titleInput, { target: { value: 'Test Task Title' } });
    fireEvent.change(descriptionInput, { target: { value: 'Test Task Description' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'Test Task Title',
        description: 'Test Task Description',
      });
    });
  });

  it('trims whitespace from form data', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText('Task Title');
    const descriptionInput = screen.getByLabelText('Description');
    const submitButton = screen.getByDisplayValue('Save Task');

    fireEvent.change(titleInput, { target: { value: '  Test Task Title  ' } });
    fireEvent.change(descriptionInput, { target: { value: '  Test Task Description  ' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'Test Task Title',
        description: 'Test Task Description',
      });
    });
  });

  it('calls onCancel when cancel button is clicked', () => {
    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        showCancelButton
      />
    );

    const cancelButton = screen.getByDisplayValue('Cancel');
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('displays external errors when provided', () => {
    const externalErrors = {
      title: 'External title error',
      description: 'External description error',
      general: 'General error occurred',
    };

    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        errors={externalErrors}
      />
    );

    expect(screen.getByText('External title error')).toBeInTheDocument();
    expect(screen.getByText('External description error')).toBeInTheDocument();
    expect(screen.getByText('General error occurred')).toBeInTheDocument();
  });

  it('shows loading state when submitting', () => {
    mockOnSubmit.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<TaskForm onSubmit={mockOnSubmit} isSubmitting />);

    const titleInput = screen.getByLabelText('Task Title');
    const submitButton = screen.getByDisplayValue('Save Task');

    fireEvent.change(titleInput, { target: { value: 'Test Task' } });
    fireEvent.click(submitButton);

    expect(submitButton).toHaveTextContent('Loading...');
    expect(submitButton).toBeDisabled();
    expect(titleInput).toBeDisabled();
  });

  it('resets form after successful submission', async () => {
    mockOnSubmit.mockResolvedValue(undefined);

    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText('Task Title');
    const descriptionInput = screen.getByLabelText('Description');
    const submitButton = screen.getByDisplayValue('Save Task');

    fireEvent.change(titleInput, { target: { value: 'Test Task' } });
    fireEvent.change(descriptionInput, { target: { value: 'Test Description' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(titleInput).toHaveValue('');
      expect(descriptionInput).toHaveValue('');
    });

    expect(mockOnSubmit).toHaveBeenCalledWith({
      title: 'Test Task',
      description: 'Test Description',
    });
  });

  it('displays character counts correctly', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText('Task Title');
    const descriptionInput = screen.getByLabelText('Description');

    // Initial counts
    expect(screen.getByText('0/200')).toBeInTheDocument();
    expect(screen.getByText('0/2000')).toBeInTheDocument();

    // After typing
    fireEvent.change(titleInput, { target: { value: 'Test Title' } });
    fireEvent.change(descriptionInput, { target: { value: 'Test Description' } });

    expect(screen.getByText('10/200')).toBeInTheDocument();
    expect(screen.getByText('16/2000')).toBeInTheDocument();
  });

  it('disables submit button when over limits', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText('Task Title');
    const submitButton = screen.getByDisplayValue('Save Task');

    // Over title limit
    fireEvent.change(titleInput, { target: { value: 'x'.repeat(201) } });

    expect(submitButton).toBeDisabled();
    expect(screen.getByText('201/200')).toBeInTheDocument();
  });

  it('autoFocuses input when autoFocus prop is true', () => {
    render(<TaskForm onSubmit={mockOnSubmit} autoFocus />);

    const titleInput = screen.getByLabelText('Task Title');
    expect(titleInput).toHaveFocus();
  });

  it('displays custom submit button text', () => {
    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        submitButtonText="Create New Task"
      />
    );

    expect(screen.getByDisplayValue('Create New Task')).toBeInTheDocument();
  });

  it('displays custom title', () => {
    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        title="Edit Existing Task"
      />
    );

    expect(screen.getByText('Edit Existing Task')).toBeInTheDocument();
  });
});