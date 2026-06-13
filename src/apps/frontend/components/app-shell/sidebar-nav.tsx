import clsx from 'clsx';
import React from 'react';

import NavItem, { NavItemSpec } from 'frontend/components/app-shell/nav-item';
import IconButton from 'frontend/components/icon-button';
import CloseIcon from 'frontend/components/icons/close-icon';
import Inline from 'frontend/components/layout/inline';
import Stack from 'frontend/components/layout/stack';
import Heading from 'frontend/components/typography/heading';
import { Spacing } from 'frontend/types/design-system';

interface SidebarNavProps {
  items: NavItemSpec[];
  brand: string;
  // Drawer state for the mobile breakpoint. On desktop the sidebar is always
  // visible; below `lg` it slides in as an overlay drawer.
  open: boolean;
  onClose: () => void;
  testId?: string;
}

/**
 * The application sidebar: a brand header and the primary navigation. Always
 * visible from the `lg` breakpoint up; below it, renders as a dismissible
 * drawer driven by `open` / `onClose`.
 */
const SidebarNav: React.FC<SidebarNavProps> = ({
  brand,
  items,
  onClose,
  open,
  testId,
}) => (
  <>
    {open && (
      <button
        type="button"
        aria-label="Close navigation"
        onClick={onClose}
        className="fixed inset-0 z-20 bg-black/40 lg:hidden"
      />
    )}
    <aside
      data-testid={testId}
      className={clsx(
        'fixed inset-y-0 left-0 z-30 w-64 border-r border-line-subtle bg-surface transition-transform lg:static lg:translate-x-0',
        open ? 'translate-x-0' : '-translate-x-full',
      )}
    >
      <Stack gap={Spacing.Lg} flex>
        <Inline justify="between" align="center" padding={Spacing.Md}>
          <Heading level={1}>{brand}</Heading>
          <span className="lg:hidden">
            <IconButton
              label="Close navigation"
              icon={<CloseIcon />}
              onClick={onClose}
            />
          </span>
        </Inline>
        <nav className="px-3">
          <Stack gap={Spacing.Xs}>
            {items.map((item) => (
              <NavItem key={item.path} item={item} onNavigate={onClose} />
            ))}
          </Stack>
        </nav>
      </Stack>
    </aside>
  </>
);

export default SidebarNav;
