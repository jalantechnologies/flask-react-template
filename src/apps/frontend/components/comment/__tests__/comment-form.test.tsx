import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CommentForm from '../comment-form.component';

// Mock the Button component
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
}));

// Mock typography
jest.mock('frontend/components/typography', () => ({
  ParagraphMedium: ({ children }: any) => <p>{children}</p>,
}));

describe('CommentForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders form with required elements', () => {
    render(<CommentForm onSubmit={mockOnSubmit} />);

    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Post Comment')).toBeInTheDocument();
    expect(screen.getByText('2000 characters remaining')).toBeInTheDocument();
  });

  it('updates character count as user types', () => {
    render(<CommentForm onSubmit={mockOnSubmit} />);

    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'Hello world' } });

    expect(screen.getByText('1987 characters remaining')).toBeInTheDocument();
  });

  it('calls onSubmit when valid comment is submitted', async () => {
    render(<CommentForm onSubmit={mockOnSubmit} />);

    const textarea = screen.getByRole('textbox');
    const submitButton = screen.getByDisplayValue('Post Comment');

    fireEvent.change(textarea, { target: { value: 'This is a test comment' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('This is a test comment');
    });
  });

  it('trims whitespace from submitted comment', async () => {
    render(<CommentForm onSubmit={mockOnSubmit} />);

    const textarea = screen.getByRole('textbox');
    const submitButton = screen.getByDisplayValue('Post Comment');

    fireEvent.change(textarea, { target: { value: '  This is a test comment  ' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('This is a test comment');
    });
  });

  it('shows error when trying to submit empty comment', async () => {
    render(<CommentForm onSubmit={mockOnSubmit} />);

    const textarea = screen.getByRole('textbox');
    const submitButton = screen.getByDisplayValue('Post Comment');

    fireEvent.change(textarea, { target: { value: '   ' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Comment cannot be empty');
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('disables submit button when over character limit', () => {
    render(<CommentForm onSubmit={mockOnSubmit} />);

    const textarea = screen.getByRole('textbox');
    const submitButton = screen.getByDisplayValue('Post Comment');

    // Create a string longer than 2000 characters
    const longContent = 'x'.repeat(2001);
    fireEvent.change(textarea, { target: { value: longContent } });

    expect(submitButton).toBeDisabled();
    expect(screen.getByText('-1 characters remaining')).toBeInTheDocument();
  });

  it('calls onCancel when cancel button is clicked', () => {
    const mockOnCancel = jest.fn();
    render(<CommentForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} showCancelButton />);

    const cancelButton = screen.getByDisplayValue('Cancel');
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('shows loading state when submitting', () => {
    mockOnSubmit.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<CommentForm onSubmit={mockOnSubmit} isSubmitting />);

    const submitButton = screen.getByTestId('button');
    expect(submitButton).toHaveTextContent('Loading...');
    expect(submitButton).toBeDisabled();
  });

  it('resets form after successful submission', async () => {
    mockOnSubmit.mockResolvedValue(undefined);

    render(<CommentForm onSubmit={mockOnSubmit} />);

    const textarea = screen.getByRole('textbox');
    const submitButton = screen.getByDisplayValue('Post Comment');

    fireEvent.change(textarea, { target: { value: 'Test comment' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(textarea).toHaveValue('');
      expect(screen.getByText('2000 characters remaining')).toBeInTheDocument();
    });
  });
});