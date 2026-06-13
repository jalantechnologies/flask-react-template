import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

import { GAP_CLASS } from 'frontend/components/layout/spacing-classes';
import { Spacing } from 'frontend/types/design-system';

type GridCols = 1 | 2 | 3 | 4;

interface GridProps {
  // Responsive column count: collapses to `base` on mobile, widening at the
  // `sm` (640px) and `md` (768px) breakpoints when set.
  base?: GridCols;
  sm?: GridCols;
  md?: GridCols;
  gap?: Spacing;
  testId?: string;
}

const COLS_CLASS: Record<GridCols, string> = {
  1: 'grid-cols-1',
  2: 'grid-cols-2',
  3: 'grid-cols-3',
  4: 'grid-cols-4',
};

const SM_COLS_CLASS: Record<GridCols, string> = {
  1: 'sm:grid-cols-1',
  2: 'sm:grid-cols-2',
  3: 'sm:grid-cols-3',
  4: 'sm:grid-cols-4',
};

const MD_COLS_CLASS: Record<GridCols, string> = {
  1: 'md:grid-cols-1',
  2: 'md:grid-cols-2',
  3: 'md:grid-cols-3',
  4: 'md:grid-cols-4',
};

/**
 * A responsive grid with a standard gap token. Replaces ad-hoc
 * `grid grid-cols-2 md:grid-cols-4 gap-3` in summary-card rows.
 */
const Grid: React.FC<PropsWithChildren<GridProps>> = ({
  base = 1,
  children,
  gap = Spacing.Md,
  md,
  sm,
  testId,
}) => (
  <div
    data-testid={testId}
    className={clsx(
      'grid',
      COLS_CLASS[base],
      sm && SM_COLS_CLASS[sm],
      md && MD_COLS_CLASS[md],
      GAP_CLASS[gap],
    )}
  >
    {children}
  </div>
);

export default Grid;
