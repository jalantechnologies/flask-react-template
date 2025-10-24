import { createBrowserRouter } from '@datadog/browser-rum-react/react-router-v6';
import React from 'react';
import { RouterProvider } from 'react-router-dom';

import { useAuthContext } from 'frontend/contexts';
import { protectedRoutes } from 'frontend/routes/protected';
import { publicRoutes } from 'frontend/routes/public';

export const AppRoutes = () => {
  const { isUserAuthenticated } = useAuthContext();

  const routes = isUserAuthenticated() ? protectedRoutes : publicRoutes;

  const router = createBrowserRouter(routes);

  return <RouterProvider router={router} />;
};
