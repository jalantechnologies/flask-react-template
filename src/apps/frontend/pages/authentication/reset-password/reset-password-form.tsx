import React from 'react';

import {
  Button,
  PasswordStrengthMeter,
  Spacing,
  Stack,
  TextField,
  Variant,
} from 'frontend/components';
import useResetPasswordForm from 'frontend/pages/authentication/reset-password/reset-password-form.hook';
import { AsyncError } from 'frontend/types';
import { ButtonType } from 'frontend/types/button';
import { getPasswordMinScore } from 'frontend/utils/password-strength';

interface ResetPasswordFormProps {
  onSuccess: () => void;
  onError: (error: AsyncError) => void;
}

const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({
  onSuccess,
  onError,
}) => {
  const { formik, isResetPasswordLoading } = useResetPasswordForm({
    onSuccess,
    onError,
  });

  return (
    <form onSubmit={formik.handleSubmit}>
      <Stack gap={Spacing.Md}>
        <Stack gap={Spacing.Xs}>
          <TextField
            testId="password"
            label="Password"
            type="password"
            name="password"
            autoComplete="new-password"
            disabled={isResetPasswordLoading}
            value={formik.values.password}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.password ? formik.errors.password : ''}
            placeholder="Enter your new password"
          />
          <PasswordStrengthMeter
            testId="password-strength"
            password={formik.values.password}
            minScore={getPasswordMinScore()}
          />
        </Stack>
        <TextField
          testId="confirmPassword"
          label="Re-type Password"
          type="password"
          name="confirmPassword"
          autoComplete="new-password"
          disabled={isResetPasswordLoading}
          value={formik.values.confirmPassword}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={
            formik.touched.confirmPassword ? formik.errors.confirmPassword : ''
          }
          placeholder="Re-enter the password"
        />
        <Button
          isLoading={isResetPasswordLoading}
          variant={Variant.Primary}
          fullWidth
          type={ButtonType.SUBMIT}
        >
          Reset Password
        </Button>
      </Stack>
    </form>
  );
};

export default ResetPasswordForm;
