import React, { useEffect } from 'react';
import toast from 'react-hot-toast';
import { Outlet, useNavigate } from 'react-router-dom';

import routes from 'frontend/constants/routes';
import { useAccountContext, useAuthContext } from 'frontend/contexts';
import { Dashboard, NotFound, TaskDetail, TaskCreate, TaskEdit } from 'frontend/pages';
import AppLayout from 'frontend/pages/app-layout/app-layout';
import { AsyncError } from 'frontend/types';

const App = () => {
  const { getAccountDetails } = useAccountContext();
  const { logout } = useAuthContext();
  const navigate = useNavigate();

  useEffect(() => {
    getAccountDetails().catch((err: AsyncError) => {
      toast.error(err.message);
      logout();
      navigate(routes.LOGIN);
    });
  }, [getAccountDetails, logout, navigate]);

  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
  );
};

const TaskDetailWrapper = () => {
  const { accessToken } = useAuthContext();
  return <TaskDetail accessToken={accessToken} />;
};

const TaskCreateWrapper = () => {
  return <TaskCreate />;
};

const TaskEditWrapper = () => {
  return <TaskEdit />;
};

export const protectedRoutes = [
  {
    path: '',
    element: <App />,
    children: [
      { path: '', element: <Dashboard /> },
      { path: 'tasks/create', element: <TaskCreateWrapper /> },
      { path: 'tasks/:taskId/edit', element: <TaskEditWrapper /> },
      { path: 'tasks/:taskId', element: <TaskDetailWrapper /> },
      { path: '*', element: <NotFound /> },
    ],
  },
];
