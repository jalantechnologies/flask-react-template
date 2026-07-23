import React, { PropsWithChildren } from 'react';
import { useNavigate } from 'react-router-dom';

import { AppShell, NavItemSpec } from 'frontend/components';
import DashboardIcon from 'frontend/components/icons/dashboard-icon';
import KeyIcon from 'frontend/components/icons/key-icon';
import routes from 'frontend/constants/routes';
import { useAccountContext, useAuthContext } from 'frontend/contexts';

const NAV_ITEMS: NavItemSpec[] = [
  {
    icon: <DashboardIcon />,
    label: 'Dashboard',
    path: routes.DASHBOARD,
  },
  {
    icon: <KeyIcon />,
    label: 'API keys',
    path: routes.API_KEYS,
  },
];

export const AppLayout: React.FC<PropsWithChildren> = ({ children }) => {
  const navigate = useNavigate();
  const { logout } = useAuthContext();
  const { accountDetails } = useAccountContext();

  const handleSignOut = () => {
    logout();
    navigate(routes.LOGIN);
  };

  return (
    <AppShell
      brand="Better"
      logoSrc="/assets/img/better-logo.png"
      navItems={NAV_ITEMS}
      userName={accountDetails.displayName()}
      userEmail={accountDetails.username}
      onSignOut={handleSignOut}
    >
      {children}
    </AppShell>
  );
};

export default AppLayout;
