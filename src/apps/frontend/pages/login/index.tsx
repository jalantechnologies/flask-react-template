import React from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

import LoginForm from './login-form';

import { Heading, Stack, Spacing } from 'frontend/components';
import routes from 'frontend/constants/routes';
import AuthenticationFormLayout from 'frontend/pages/authentication/authentication-form-layout';
import AuthenticationPageLayout from 'frontend/pages/authentication/authentication-page-layout';
import { AsyncError } from 'frontend/types';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const onSuccess = () => {
    navigate(routes.DASHBOARD);
  };

  const onError = (error: AsyncError) => {
    toast.error(error.message);
  };

  return (
    <AuthenticationPageLayout>
      <AuthenticationFormLayout>
        <Stack gap={Spacing.Lg}>
          <Heading level={1}>Log In</Heading>
          <LoginForm onSuccess={onSuccess} onError={onError} />
        </Stack>
      </AuthenticationFormLayout>
    </AuthenticationPageLayout>
  );
};

export default Login;
