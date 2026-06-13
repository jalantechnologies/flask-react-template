import React, { PropsWithChildren, useState } from 'react';

import { NavItemSpec } from 'frontend/components/app-shell/nav-item';
import SidebarNav from 'frontend/components/app-shell/sidebar-nav';
import TopBar from 'frontend/components/app-shell/top-bar';

interface AppShellProps {
  brand: string;
  navItems: NavItemSpec[];
  userName: string;
  userEmail: string;
  onSignOut: () => void;
  testId?: string;
}

/**
 * The application chrome: a sidebar, a top bar, and the routed content region.
 * Pages render their content as children (typically a router <Outlet/>); the
 * shell owns the surrounding frame and the mobile navigation drawer state.
 */
const AppShell: React.FC<PropsWithChildren<AppShellProps>> = ({
  brand,
  children,
  navItems,
  onSignOut,
  testId,
  userEmail,
  userName,
}) => {
  const [isNavOpen, setIsNavOpen] = useState(false);

  return (
    <div
      data-testid={testId}
      className="flex h-screen overflow-hidden bg-surface text-content"
    >
      <SidebarNav
        brand={brand}
        items={navItems}
        open={isNavOpen}
        onClose={() => setIsNavOpen(false)}
      />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar
          userName={userName}
          userEmail={userEmail}
          onSignOut={onSignOut}
          onOpenNav={() => setIsNavOpen(true)}
        />
        <main className="flex flex-1 flex-col overflow-hidden">{children}</main>
      </div>
    </div>
  );
};

export default AppShell;
