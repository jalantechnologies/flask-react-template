import React from 'react';

import {
  Button,
  FormControl,
  Input,
  VerticalStackLayout,
} from 'frontend/components';
import ParagraphMedium from 'frontend/components/typography/paragraph-medium';
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
    <VerticalStackLayout gap={5}>
      <ParagraphMedium>
        Enter your details to receive a reset link
      </ParagraphMedium>
      <form onSubmit={formik.handleSubmit}>
        <VerticalStackLayout gap={5}>
          <FormControl
            error={formik.touched.username ? formik.errors.username : ''}
            label={'Email'}
          >
            <Input
              data-testid="username"
              disabled={isSendForgotPasswordEmailLoading}
              error={formik.touched.username ? formik.errors.username : ''}
              endEnhancer={
                <img
                  alt="email icon"
                  className="fill-current opacity-50"
                  src="assets/img/icon/email.svg"
                />
              }
              onBlur={formik.handleBlur}
              onChange={formik.handleChange}
              name="username"
              value={formik.values.username}
              placeholder="Enter your email"
            />
          </FormControl>

          <Button
            isLoading={isSendForgotPasswordEmailLoading}
            type={ButtonType.SUBMIT}
          >
            Receive Reset Link
          </Button>
        </VerticalStackLayout>
      </form>
    </VerticalStackLayout>
  );
};

export default ForgotPasswordForm;
