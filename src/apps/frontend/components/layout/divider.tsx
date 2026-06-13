import clsx from 'clsx';
import React from 'react';

interface DividerProps {
  orientation?: 'horizontal' | 'vertical';
  testId?: string;
}

/** A one-pixel rule in the theme's line color. */
const Divider: React.FC<DividerProps> = ({
  orientation = 'horizontal',
  testId,
}) => (
  <hr
    aria-orientation={orientation}
    data-testid={testId}
    className={clsx(
      'border-0 bg-line',
      orientation === 'horizontal' ? 'h-px w-full' : 'h-full w-px',
    )}
  />
);

export default Divider;
