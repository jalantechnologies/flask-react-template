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
import constant from 'frontend/constants';
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

  const resendPasswordResetEmail = async () => {
    try {
      await sendForgotPasswordEmail(username);
      onSuccess();
    } catch (error) {
      onError(error as AsyncError);
    }
  };

  const handleResendPasswordResetEmail = (e: React.FormEvent<EventTarget>) => {
    e.preventDefault();
    void resendPasswordResetEmail();
  };

  return (
    <Stack gap={Spacing.Md}>
      <Text testId="password-reset-confirmation">
        {constant.PASSWORD_RESET_LINK_SENT_MESSAGE}
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
