import React, { PropsWithChildren } from 'react';

type Breakpoint = 'mobile' | 'desktop';
type Display = 'block' | 'flex' | 'flexCol';

interface ShowProps {
  // 'mobile' renders only below the md breakpoint; 'desktop' renders only at
  // md and up. This is the single place breakpoint visibility is expressed,
  // so pages stop hand-writing `hidden md:block` / `md:hidden`.
  on: Breakpoint;
  // Layout of the visible wrapper. `block` is the default; `flex` / `flexCol`
  // keep the children laid out when shown.
  display?: Display;
  testId?: string;
}

const VISIBILITY_CLASS: Record<Breakpoint, Record<Display, string>> = {
  desktop: {
    block: 'hidden md:block',
    flex: 'hidden md:flex',
    flexCol: 'hidden md:flex md:flex-col',
  },
  mobile: {
    block: 'block md:hidden',
    flex: 'flex md:hidden',
    flexCol: 'flex flex-col md:hidden',
  },
};

/**
 * Responsive visibility. Renders its children only on the given breakpoint.
 * Use it for the desktop-table / mobile-card split instead of raw
 * `hidden md:block` classes on a page.
 */
const Show: React.FC<PropsWithChildren<ShowProps>> = ({
  children,
  display = 'block',
  on,
  testId,
}) => (
  <div data-testid={testId} className={VISIBILITY_CLASS[on][display]}>
    {children}
  </div>
);

export default Show;
