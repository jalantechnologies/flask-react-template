import React from 'react';
import toast from 'react-hot-toast';

import { Heading, Spacing, Stack } from 'frontend/components';
import AuthenticationFormLayout from 'frontend/pages/authentication/authentication-form-layout';
import AuthenticationPageLayout from 'frontend/pages/authentication/authentication-page-layout';
import PhoneLoginForm from 'frontend/pages/authentication/phone-login/phone-login-form';
import { AsyncError } from 'frontend/types';

export const PhoneLogin: React.FC = () => {
  const onSendOTPSuccess = () => {
    toast.success(
      'OTP has been sent successfully. Please check your messages.',
    );
  };

  const onError = (error: AsyncError) => {
    toast.error(error.message);
  };

  return (
    <AuthenticationPageLayout>
      <AuthenticationFormLayout>
        <Stack gap={Spacing.Lg}>
          <Heading level={1}>Log In</Heading>
          <PhoneLoginForm
            onError={onError}
            onSendOTPSuccess={onSendOTPSuccess}
          />
        </Stack>
      </AuthenticationFormLayout>
    </AuthenticationPageLayout>
  );
};

export default PhoneLogin;
