import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { describe, expect, it, vi } from 'vitest';

import ConfirmDialog from 'frontend/components/confirm-dialog';

describe('ConfirmDialog', () => {
  it('renders its message and confirms', async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();

    render(
      <ConfirmDialog
        testId="confirm"
        title="Delete task"
        message="This cannot be undone."
        onConfirm={onConfirm}
        onCancel={vi.fn()}
      />,
    );

    const dialog = screen.getByTestId('confirm');
    expect(dialog).toHaveAttribute('open');
    expect(dialog).toHaveProperty('open', true);
    expect(screen.getByText('This cannot be undone.')).toBeVisible();

    await user.click(screen.getByRole('button', { name: 'Confirm' }));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('drops the open attribute when it unmounts', () => {
    const { unmount } = render(
      <ConfirmDialog
        testId="confirm"
        title="Delete task"
        message="This cannot be undone."
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
      />,
    );

    const dialog = screen.getByTestId('confirm');
    expect(dialog).toHaveAttribute('open');

    unmount();

    expect(dialog).not.toHaveAttribute('open');
    expect(dialog).toHaveProperty('open', false);
  });

  it('cancels without leaking the previous render', async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();

    render(
      <ConfirmDialog
        testId="confirm"
        title="Delete task"
        message="This cannot be undone."
        onConfirm={vi.fn()}
        onCancel={onCancel}
      />,
    );

    expect(screen.getByTestId('confirm')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
