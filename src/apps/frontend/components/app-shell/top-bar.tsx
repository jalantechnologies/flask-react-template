import React from 'react';

import UserMenu from 'frontend/components/app-shell/user-menu';
import IconButton from 'frontend/components/icon-button';
import MenuIcon from 'frontend/components/icons/menu-icon';
import Inline from 'frontend/components/layout/inline';
import { Spacing } from 'frontend/types/design-system';

interface TopBarProps {
  userName: string;
  userEmail: string;
  onSignOut: () => void;
  // Opens the navigation drawer on the mobile breakpoint.
  onOpenNav: () => void;
  testId?: string;
}

/**
 * The top bar inside the app shell: a navigation toggle on mobile and the
 * signed-in user menu. Sits above the routed page content.
 */
const TopBar: React.FC<TopBarProps> = ({
  onOpenNav,
  onSignOut,
  testId,
  userEmail,
  userName,
}) => (
  <header
    data-testid={testId}
    className="shrink-0 border-b border-line-subtle bg-surface px-4 py-3"
  >
    <Inline justify="between" align="center">
      <span className="lg:hidden">
        <IconButton
          label="Open navigation"
          icon={<MenuIcon />}
          onClick={onOpenNav}
        />
      </span>
      <Inline gap={Spacing.Md} align="center" justify="end" flex>
        <UserMenu name={userName} email={userEmail} onSignOut={onSignOut} />
      </Inline>
    </Inline>
  </header>
);

export default TopBar;
