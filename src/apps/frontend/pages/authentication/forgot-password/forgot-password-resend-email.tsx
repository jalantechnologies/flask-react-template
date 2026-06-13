import React from 'react';

import {
  Button,
  Emphasis,
  Inline,
  Spacing,
  Stack,
  Text,
  Variant,
} from 'frontend/components';
import { useResetPasswordContext } from 'frontend/contexts';
import { AsyncError } from 'frontend/types';
import { ButtonType } from 'frontend/types/button';

interface ForgotPasswordResendEmailProps {
  isResendEnabled: boolean;
  onError: (error: AsyncError) => void;
  onSuccess: () => void;
  timerRemainingSeconds: string;
  username: string;
}

const ForgotPasswordResendEmail: React.FC<ForgotPasswordResendEmailProps> = ({
  isResendEnabled,
  onError,
  onSuccess,
  timerRemainingSeconds,
  username,
}) => {
  const { isSendForgotPasswordEmailLoading, sendForgotPasswordEmail } =
    useResetPasswordContext();

  const handleResendPasswordResetEmail = (e: React.FormEvent<EventTarget>) => {
    e.preventDefault();
    sendForgotPasswordEmail(username)
      .then(() => {
        onSuccess();
      })
      .catch((error: AsyncError) => {
        onError(error);
      });
  };

  return (
    <Stack gap={Spacing.Md}>
      <Text>
        A password reset link has been sent to {username}. Please check your
        inbox and follow the instructions.
      </Text>
      {!isResendEnabled && (
        <Inline justify="end">
          <Text emphasis={Emphasis.Muted}>
            Resend email in 00: {timerRemainingSeconds}
          </Text>
        </Inline>
      )}
      <form onSubmit={handleResendPasswordResetEmail}>
        <Button
          disabled={!isResendEnabled}
          isLoading={isSendForgotPasswordEmailLoading}
          variant={Variant.Primary}
          fullWidth
          type={ButtonType.SUBMIT}
        >
          Resend Link
        </Button>
      </form>
    </Stack>
  );
};

export default ForgotPasswordResendEmail;
