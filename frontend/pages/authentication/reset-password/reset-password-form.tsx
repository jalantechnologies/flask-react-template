import React from 'react';

import {
  Button,
  FormControl,
  PasswordInput,
  VerticalStackLayout,
} from 'frontend/components';
import useResetPasswordForm from 'frontend/pages/authentication/reset-password/reset-password-form.hook';
import { AsyncError } from 'frontend/types';
import { ButtonType } from 'frontend/types/button';

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
      <VerticalStackLayout gap={5}>
        <FormControl
          error={formik.touched.password ? formik.errors.password : ''}
          label={'Password'}
        >
          <PasswordInput
            data-testid="password"
            disabled={isResetPasswordLoading}
            error={formik.touched.password ? formik.errors.password : ''}
            name="password"
            onBlur={formik.handleBlur}
            onChange={formik.handleChange}
            value={formik.values.password}
            placeholder="Enter your new password"
          />
        </FormControl>

        <FormControl
          error={
            formik.touched.confirmPassword ? formik.errors.confirmPassword : ''
          }
          label={'Re-type Password'}
        >
          <PasswordInput
            data-testid="confirmPassword"
            disabled={isResetPasswordLoading}
            error={
              formik.touched.confirmPassword
                ? formik.errors.confirmPassword
                : ''
            }
            name="confirmPassword"
            onBlur={formik.handleBlur}
            onChange={formik.handleChange}
            value={formik.values.confirmPassword}
            placeholder="Re-enter the password"
          />
        </FormControl>

        <Button isLoading={isResetPasswordLoading} type={ButtonType.SUBMIT}>
          Reset Password
        </Button>
      </VerticalStackLayout>
    </form>
  );
};

export default ResetPasswordForm;
