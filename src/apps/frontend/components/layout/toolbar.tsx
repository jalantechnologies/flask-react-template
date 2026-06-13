import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

interface ToolbarProps {
  // A horizontal bar with a bottom border, used for page filters and actions.
  border?: 'bottom' | 'top' | 'none';
  align?: 'center' | 'end';
  testId?: string;
}

/**
 * A bordered horizontal bar for page-level controls (filters, actions, counts).
 * Replaces the repeated `flex items-center justify-between border-b px-6 py-3`.
 */
const Toolbar: React.FC<PropsWithChildren<ToolbarProps>> = ({
  align = 'center',
  border = 'bottom',
  children,
  testId,
}) => (
  <div
    data-testid={testId}
    className={clsx(
      'flex shrink-0 flex-wrap justify-between gap-3 px-6 py-3',
      align === 'center' ? 'items-center' : 'items-end',
      border === 'bottom' && 'border-b border-line-subtle',
      border === 'top' && 'border-t border-line-subtle',
    )}
  >
    {children}
  </div>
);

export default Toolbar;
