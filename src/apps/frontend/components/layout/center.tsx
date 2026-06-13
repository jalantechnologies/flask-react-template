import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

interface CenterProps {
  // Centers content both axes. `fill` grows to the parent; `minHeight` gives
  // a comfortable default for empty / loading states.
  fill?: boolean;
  minHeight?: boolean;
  testId?: string;
}

/**
 * Centers its children horizontally and vertically. Used for loading and
 * empty states that were each re-writing `flex h-32 items-center justify-center`.
 */
const Center: React.FC<PropsWithChildren<CenterProps>> = ({
  children,
  fill = false,
  minHeight = true,
  testId,
}) => (
  <div
    data-testid={testId}
    className={clsx(
      'flex items-center justify-center',
      fill && 'flex-1',
      minHeight && 'min-h-32',
    )}
  >
    {children}
  </div>
);

export default Center;
