import React from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

import { Heading, Spacing, Stack, Text } from 'frontend/components';
import routes from 'frontend/constants/routes';
import AuthenticationFormLayout from 'frontend/pages/authentication/authentication-form-layout';
import AuthenticationPageLayout from 'frontend/pages/authentication/authentication-page-layout';
import ResetPasswordForm from 'frontend/pages/authentication/reset-password/reset-password-form';
import { AsyncError } from 'frontend/types';

export const ResetPassword: React.FC = () => {
  const navigate = useNavigate();

  const onSuccess = () => {
    toast.success(
      'Your password has been successfully updated. Please login to continue.',
    );
    navigate(routes.LOGIN);
  };

  const onError = (error: AsyncError) => {
    toast.error(error.message);
  };

  return (
    <AuthenticationPageLayout>
      <AuthenticationFormLayout>
        <Stack gap={Spacing.Md}>
          <Heading level={1}>Reset Password</Heading>
          <Text>Setup your new password here</Text>
          <ResetPasswordForm onSuccess={onSuccess} onError={onError} />
        </Stack>
      </AuthenticationFormLayout>
    </AuthenticationPageLayout>
  );
};

export default ResetPassword;
