import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

import { Button, H2, VerticalStackLayout } from 'frontend/components';
import routes from 'frontend/constants/routes';
import AuthenticationPageLayout from 'frontend/pages/authentication//authentication-page-layout';
import AuthenticationFormLayout from 'frontend/pages/authentication/authentication-form-layout';
import ForgotPasswordForm from 'frontend/pages/authentication/forgot-password/forgot-password-form';
import ForgotPasswordResendEmail from 'frontend/pages/authentication/forgot-password/forgot-password-resend-email';
import { AsyncError } from 'frontend/types';
import { ButtonKind } from 'frontend/types/button';
import useTimer from 'frontend/utils/use-timer.hook';

export const ForgotPassword: React.FC = () => {
  const passwordResendDelayInSeconds = 60_000;

  const navigate = useNavigate();

  const [isResendEmailPage, setIsResendEmailPage] = useState(false);
  const [username, setUsername] = useState('');

  const { startTimer, remaininingSecondsStr, isResendEnabled } = useTimer({
    delayInMilliseconds: passwordResendDelayInSeconds,
  });

  const onSendEmailSuccess = (newUsername: string) => {
    startTimer();
    setUsername(newUsername);
    setIsResendEmailPage(true);
  };

  const onResendEmailSuccess = () => {
    startTimer();
    toast.success(
      'A password reset link has been re-sent. Please check your inbox',
    );
  };

  const onError = (error: AsyncError) => {
    toast.error(error.message);
  };

  const handleBackButtonClick = () => {
    if (isResendEmailPage) {
      setIsResendEmailPage(false);
    } else {
      navigate(routes.LOGIN);
    }
  };

  return (
    <AuthenticationPageLayout>
      <AuthenticationFormLayout>
        <VerticalStackLayout gap={6}>
          <Button kind={ButtonKind.SECONDARY} onClick={handleBackButtonClick}>
            Back
          </Button>
          <H2>Forgot Password?</H2>
          {isResendEmailPage ? (
            <ForgotPasswordResendEmail
              isResendEnabled={isResendEnabled}
              onSuccess={onResendEmailSuccess}
              onError={onError}
              username={username}
              timerRemainingSeconds={remaininingSecondsStr}
            />
          ) : (
            <ForgotPasswordForm
              onSuccess={onSendEmailSuccess}
              onError={onError}
            />
          )}
        </VerticalStackLayout>
      </AuthenticationFormLayout>
    </AuthenticationPageLayout>
  );
};

export default ForgotPassword;
