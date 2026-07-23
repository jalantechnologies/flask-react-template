import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { describe, expect, it, vi } from 'vitest';

import Button from 'frontend/components/button';

describe('Button', () => {
  it('renders its label and calls onClick when pressed', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();

    render(
      <Button testId="save" onClick={onClick}>
        Save
      </Button>,
    );

    const button = screen.getByTestId('save');
    expect(button).toHaveTextContent('Save');

    await user.click(button);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled and does not fire onClick while loading', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();

    render(
      <Button testId="save" isLoading onClick={onClick}>
        Save
      </Button>,
    );

    const button = screen.getByTestId('save');
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
    expect(button).not.toHaveTextContent('Save');

    await user.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  it('does not fire onClick when disabled', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();

    render(
      <Button testId="save" disabled onClick={onClick}>
        Save
      </Button>,
    );

    await user.click(screen.getByTestId('save'));
    expect(onClick).not.toHaveBeenCalled();
  });
});
