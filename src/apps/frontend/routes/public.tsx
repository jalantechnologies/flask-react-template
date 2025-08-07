import React from 'react';
import { Navigate } from 'react-router-dom';

import routes from '../constants/routes';
import constant from '../constants';
import { ResetPasswordProvider } from '../contexts';
import { Config } from '../helpers';
import {
  About,
  Login,
  Signup,
  ForgotPassword,
  ResetPassword,
  OTPVerificationPage,
  PhoneLogin,
  Dashboard,
} from '../pages';
import TaskDetails from '../pages/task-details'; // 👈 The correct way to import TaskDetails

const currentAuthMechanism = Config.getConfigValue<string>(
  'authenticationMechanism',
);

export const publicRoutes = [
  // Default route will now go to the Dashboard
  { path: '/', element: <Navigate to={routes.DASHBOARD} /> },
  { path: routes.DASHBOARD, element: <Dashboard /> },
  { path: routes.ABOUT, element: <About /> },
  { path: '/tasks/:taskId', element: <TaskDetails /> }, // The dynamic task details page

  {
    path: routes.FORGOT_PASSWORD,
    element: (
      <ResetPasswordProvider>
        <ForgotPassword />
      </ResetPasswordProvider>
    ),
  },
  {
    path: routes.RESET_PASSWORD,
    element: (
      <ResetPasswordProvider>
        <ResetPassword />
      </ResetPasswordProvider>
    ),
  },
  // This catch-all route now redirects to the dashboard
  { path: '*', element: <Navigate to={routes.DASHBOARD} /> },
];

if (currentAuthMechanism === constant.PHONE_NUMBER_BASED_AUTHENTICATION) {
  publicRoutes.push(
    { path: routes.LOGIN, element: <PhoneLogin /> },
    { path: routes.VERIFY_OTP, element: <OTPVerificationPage /> },
  );
}

if (currentAuthMechanism === constant.EMAIL_BASED_AUTHENTICATION) {
  publicRoutes.push(
    { path: routes.LOGIN, element: <Login /> },
    { path: routes.SIGNUP, element: <Signup /> },
  );
}