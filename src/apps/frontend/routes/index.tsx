import React from 'react';
import { BrowserRouter, Route, Routes as ReactRoutes } from 'react-router-dom';

import { publicRoutes } from './public';
import { protectedRoutes } from './protected';

// This is the main router component that determines which routes to show.
export const AppRoutes: React.FC = () => {
  // You would add logic here to check if the user is authenticated.
  // For now, we'll just render the public routes so you can see your work.
  const isAuth = false; // We'll hardcode this to false for now

  // Here, we combine public and protected routes based on authentication.
  // We will remove the protected routes for now to avoid the login redirect.
  const allRoutes = isAuth ? [...publicRoutes, ...protectedRoutes] : publicRoutes;

  return (
    <BrowserRouter>
      <ReactRoutes>
        {allRoutes.map((route, index) => (
          <Route key={index} path={route.path} element={route.element} />
        ))}
      </ReactRoutes>
    </BrowserRouter>
  );
};