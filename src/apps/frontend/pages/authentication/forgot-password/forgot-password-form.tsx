import React from 'react';

import {
  Button,
  Spacing,
  Stack,
  Text,
  TextField,
  Variant,
} from 'frontend/components';
import useForgotPasswordForm from 'frontend/pages/authentication/forgot-password/forgot-password-form.hook';
import { AsyncError } from 'frontend/types';
import { ButtonType } from 'frontend/types/button';

interface ForgotPasswordFormProps {
  onError: (error: AsyncError) => void;
  onSuccess: (username: string) => void;
}

const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({
  onError,
  onSuccess,
}) => {
  const { formik, isSendForgotPasswordEmailLoading } = useForgotPasswordForm({
    onError,
    onSuccess,
  });

  return (
    <Stack gap={Spacing.Md}>
      <Text>Enter your details to receive a reset link</Text>
      <form onSubmit={formik.handleSubmit}>
        <Stack gap={Spacing.Md}>
          <TextField
            testId="username"
            label="Email"
            type="email"
            name="username"
            autoComplete="email"
            disabled={isSendForgotPasswordEmailLoading}
            value={formik.values.username}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.username ? formik.errors.username : ''}
            placeholder="Enter your email"
          />
          <Button
            type={ButtonType.SUBMIT}
            variant={Variant.Primary}
            fullWidth
            isLoading={isSendForgotPasswordEmailLoading}
          >
            Receive Reset Link
          </Button>
        </Stack>
      </form>
    </Stack>
  );
};

export default ForgotPasswordForm;
