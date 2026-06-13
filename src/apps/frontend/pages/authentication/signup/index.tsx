import React from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

import { Heading, Spacing, Stack } from 'frontend/components';
import routes from 'frontend/constants/routes';
import AuthenticationFormLayout from 'frontend/pages/authentication/authentication-form-layout';
import AuthenticationPageLayout from 'frontend/pages/authentication/authentication-page-layout';
import SignupForm from 'frontend/pages/authentication/signup/signup-form';
import { AsyncError } from 'frontend/types';

export const Signup: React.FC = () => {
  const navigate = useNavigate();
  const onSuccess = () => {
    toast.success(
      'Your account has been successfully created. Please login to continue.',
    );
    navigate(routes.LOGIN);
  };

  const onError = (error: AsyncError) => {
    toast.error(error.message);
  };

  return (
    <AuthenticationPageLayout>
      <AuthenticationFormLayout>
        <Stack gap={Spacing.Lg}>
          <Heading level={1}>Sign Up</Heading>
          <SignupForm onSuccess={onSuccess} onError={onError} />
        </Stack>
      </AuthenticationFormLayout>
    </AuthenticationPageLayout>
  );
};

export default Signup;
