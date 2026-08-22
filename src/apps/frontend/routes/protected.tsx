import React, { useEffect } from 'react';
import toast from 'react-hot-toast';
import { Navigate, Outlet, useNavigate } from 'react-router-dom';

import constant from 'frontend/constants';
import routes from 'frontend/constants/routes';
import { useAccountContext, useAuthContext } from 'frontend/contexts';
import { Config } from 'frontend/helpers';
import { Dashboard, NotFound } from 'frontend/pages';
import AppLayout from 'frontend/pages/app-layout/app-layout';
import { AsyncError } from 'frontend/types';

const currentAuthMechanism = Config.getConfigValue<string>(
  'authenticationMechanism',
);

const authEntryPaths = [routes.LOGIN];

if (currentAuthMechanism === constant.PHONE_NUMBER_BASED_AUTHENTICATION) {
  authEntryPaths.push(routes.VERIFY_OTP);
}

if (currentAuthMechanism === constant.EMAIL_BASED_AUTHENTICATION) {
  authEntryPaths.push(routes.SIGNUP);
}

const authEntryRedirects = authEntryPaths.map((path) => ({
  path,
  element: <Navigate to={routes.DASHBOARD} replace />,
}));

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

export const protectedRoutes = [
  {
    path: '',
    element: <App />,
    children: [
      { path: '', element: <Dashboard /> },
      ...authEntryRedirects,
      { path: '*', element: <NotFound /> },
    ],
  },
];
