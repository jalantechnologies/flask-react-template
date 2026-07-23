import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { describe, expect, it, vi } from 'vitest';

import TextField from 'frontend/components/text-field';

describe('TextField', () => {
  it('associates its label with the input and reports typed characters', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();

    render(
      <TextField testId="email" label="Email" value="" onChange={onChange} />,
    );

    const input = screen.getByTestId('email');
    expect(screen.getByLabelText('Email')).toBe(input);

    await user.type(input, 'a');
    expect(onChange).toHaveBeenCalled();
  });

  it('marks the control invalid and shows the message when given an error', () => {
    render(
      <TextField
        testId="email"
        label="Email"
        error="Please enter a valid email"
        value=""
        onChange={vi.fn()}
      />,
    );

    const input = screen.getByTestId('email');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAccessibleDescription('Please enter a valid email');
    expect(screen.getByText('Please enter a valid email')).toBeInTheDocument();
  });

  it('reflects the controlled value it is given', () => {
    render(
      <TextField
        testId="email"
        label="Email"
        value="user@example.com"
        onChange={vi.fn()}
      />,
    );

    expect(screen.getByTestId('email')).toHaveValue('user@example.com');
  });
});
