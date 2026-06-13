import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

interface PageProps {
  // When true, the page fills the app-shell content area and scrolls its body
  // internally. This is the common case for list/table screens.
  fill?: boolean;
  testId?: string;
}

/**
 * Top-level page container rendered inside the app shell's content slot.
 * Standardises the `flex flex-1 flex-col` chrome every screen was repeating.
 */
const Page: React.FC<PropsWithChildren<PageProps>> = ({
  children,
  fill = true,
  testId,
}) => (
  <div
    data-testid={testId}
    className={clsx(
      'flex flex-col',
      fill ? 'flex-1 overflow-hidden' : 'w-full',
    )}
  >
    {children}
  </div>
);

export default Page;
