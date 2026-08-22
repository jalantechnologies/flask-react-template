import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { describe, expect, it, vi } from 'vitest';

import Modal from 'frontend/components/modal';

describe('Modal', () => {
  it('renders its title and content in an open dialog', () => {
    render(
      <Modal testId="modal" title="Edit task" onClose={vi.fn()}>
        <p>Task details</p>
      </Modal>,
    );

    const dialog = screen.getByTestId('modal');
    expect(dialog).toHaveAttribute('open');
    expect(dialog).toHaveProperty('open', true);
    expect(screen.getByText('Edit task')).toBeVisible();
    expect(screen.getByText('Task details')).toBeVisible();
  });

  it('drops the open attribute when it unmounts', () => {
    const { unmount } = render(
      <Modal testId="modal" title="Edit task" onClose={vi.fn()}>
        <p>Task details</p>
      </Modal>,
    );

    const dialog = screen.getByTestId('modal');
    const closed = vi.fn();
    dialog.addEventListener('close', closed);

    unmount();

    expect(dialog).not.toHaveAttribute('open');
    expect(dialog).toHaveProperty('open', false);
    expect(closed).toHaveBeenCalledTimes(1);
  });

  it('renders a second time without leaking the first render', () => {
    render(
      <Modal testId="modal" title="Edit task" onClose={vi.fn()}>
        <p>Task details</p>
      </Modal>,
    );

    expect(screen.getByTestId('modal')).toBeInTheDocument();
    expect(screen.getByText('Edit task')).toBeVisible();
  });

  it('calls onClose when the close button is pressed', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    render(
      <Modal testId="modal" title="Edit task" onClose={onClose}>
        <p>Task details</p>
      </Modal>,
    );

    await user.click(screen.getByRole('button', { name: 'Close' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
