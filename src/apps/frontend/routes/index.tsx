import { createBrowserRouter } from '@datadog/browser-rum-react/react-router-v6';
import React, { useMemo } from 'react';
import { RouterProvider } from 'react-router-dom';

import { useAuthContext } from 'frontend/contexts';
import { protectedRoutes } from 'frontend/routes/protected';
import { publicRoutes } from 'frontend/routes/public';

export const AppRoutes = () => {
  const { isUserAuthenticated } = useAuthContext();
  const authenticated = isUserAuthenticated();

  // Rebuild the router whenever authentication flips, so logging in or out
  // swaps the route set (and the current view) immediately instead of leaving
  // the URL and the rendered page out of sync.
  const router = useMemo(
    () => createBrowserRouter(authenticated ? protectedRoutes : publicRoutes),
    [authenticated],
  );

  return <RouterProvider router={router} />;
};
