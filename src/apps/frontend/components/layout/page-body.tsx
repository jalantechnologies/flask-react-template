import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

import { PADDING_CLASS } from 'frontend/components/layout/spacing-classes';
import { Spacing } from 'frontend/types/design-system';

type PageBodyWidth = 'sm' | 'md' | 'lg';

interface PageBodyProps {
  // The scrollable region of a page. Pads its content and grows to fill.
  padding?: Spacing;
  // Caps the content column at a readable width for form-style pages. Omit to
  // let content span the full body.
  maxWidth?: PageBodyWidth;
  scroll?: boolean;
  testId?: string;
}

const MAX_WIDTH_CLASS: Record<PageBodyWidth, string> = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
};

/**
 * The scrollable content region of a Page. Owns padding and overflow so
 * individual screens stop re-declaring `flex-1 overflow-auto px-6 py-5`.
 */
const PageBody: React.FC<PropsWithChildren<PageBodyProps>> = ({
  children,
  maxWidth,
  padding = Spacing.Lg,
  scroll = true,
  testId,
}) => (
  <div
    data-testid={testId}
    className={clsx(
      'flex-1',
      scroll && 'overflow-auto',
      PADDING_CLASS[padding],
    )}
  >
    {maxWidth ? (
      <div className={MAX_WIDTH_CLASS[maxWidth]}>{children}</div>
    ) : (
      children
    )}
  </div>
);

export default PageBody;
