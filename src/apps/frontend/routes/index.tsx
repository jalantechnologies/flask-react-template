import { createBrowserRouter } from '@datadog/browser-rum-react/react-router-v6';
import { RouterProvider } from 'react-router-dom';

import { RouteGuard } from 'frontend/components/route-guard';
import routes from 'frontend/constants/routes';
import constant from 'frontend/constants';
import { ResetPasswordProvider } from 'frontend/contexts';
import { Config } from 'frontend/helpers';
import {
  About,
  ForgotPassword,
  Login,
  NotFound,
  OTPVerificationPage,
  PhoneLogin,
  ResetPassword,
  Signup,
  Tasks,
} from 'frontend/pages';
import AppLayout from 'frontend/pages/app-layout/app-layout';

const currentAuthMechanism = Config.getConfigValue<string>(
  'authenticationMechanism',
);

// Protected route wrapper
const ProtectedApp = () => (
  <RouteGuard requireAuth={true}>
    <AppLayout>
      <Tasks />
    </AppLayout>
  </RouteGuard>
);

// Create a single router configuration
const allRoutes = [
  // Protected routes
  {
    path: '/',
    element: <ProtectedApp />,
  },
  // Public routes
  {
    path: routes.FORGOT_PASSWORD,
    element: (
      <RouteGuard>
        <ResetPasswordProvider>
          <ForgotPassword />
        </ResetPasswordProvider>
      </RouteGuard>
    ),
  },
  {
    path: routes.RESET_PASSWORD,
    element: (
      <RouteGuard>
        <ResetPasswordProvider>
          <ResetPassword />
        </ResetPasswordProvider>
      </RouteGuard>
    ),
  },
  {
    path: routes.ABOUT,
    element: (
      <RouteGuard>
        <About />
      </RouteGuard>
    ),
  },
];

// Add auth-specific routes based on mechanism
if (currentAuthMechanism === constant.PHONE_NUMBER_BASED_AUTHENTICATION) {
  allRoutes.push(
    {
      path: routes.LOGIN,
      element: (
        <RouteGuard>
          <PhoneLogin />
        </RouteGuard>
      ),
    },
    {
      path: routes.VERIFY_OTP,
      element: (
        <RouteGuard>
          <OTPVerificationPage />
        </RouteGuard>
      ),
    },
  );
}

if (currentAuthMechanism === constant.EMAIL_BASED_AUTHENTICATION) {
  allRoutes.push(
    {
      path: routes.LOGIN,
      element: (
        <RouteGuard>
          <Login />
        </RouteGuard>
      ),
    },
    {
      path: routes.SIGNUP,
      element: (
        <RouteGuard>
          <Signup />
        </RouteGuard>
      ),
    },
  );
}

// Catch-all route
allRoutes.push({
  path: '*',
  element: <NotFound />,
});

const router = createBrowserRouter(allRoutes);

export const AppRoutes = () => {
  return <RouterProvider router={router} />;
};
