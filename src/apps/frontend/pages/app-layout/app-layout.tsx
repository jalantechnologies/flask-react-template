import React, { PropsWithChildren } from 'react';
import { useNavigate } from 'react-router-dom';

import { AppShell, NavItemSpec } from 'frontend/components';
import DashboardIcon from 'frontend/components/icons/dashboard-icon';
import TasksIcon from 'frontend/components/icons/tasks-icon';
import routes from 'frontend/constants/routes';
import { useAccountContext, useAuthContext } from 'frontend/contexts';

const NAV_ITEMS: NavItemSpec[] = [
  {
    icon: <DashboardIcon />,
    label: 'Dashboard',
    path: routes.DASHBOARD,
  },
  {
    icon: <TasksIcon />,
    label: 'Tasks',
    path: routes.TASKS,
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
      brand="Flask React"
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
