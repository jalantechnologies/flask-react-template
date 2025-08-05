import React from 'react';
import { Link } from 'react-router-dom';

import { AsyncError } from 'frontend//types';
import {
  VerticalStackLayout,
  FormControl,
  PasswordInput,
  Flex,
  Button,
  Input,
} from 'frontend/components';
import { CustomLayout } from 'frontend/components/layouts/custom-layout.component';
import { LayoutType } from 'frontend/components/layouts/layout-config';
import routes from 'frontend/constants/routes';
import LoginFormCheckbox from 'frontend/pages/login/login-form-checkbox';
import useLoginForm from 'frontend/pages/login/login-form.hook';
import { ButtonType, ButtonKind } from 'frontend/types/button';

type LoginFields = 'username' | 'password';

interface LoginFormProps {
  onSuccess: () => void;
  onError: (error: AsyncError) => void;
  layoutType?: LayoutType;
}

const LoginForm: React.FC<LoginFormProps> = ({
  onError,
  onSuccess,
  layoutType = LayoutType.Default,
}) => {
  const { formik, isLoginLoading } = useLoginForm({ onSuccess, onError });

  const getFormikError = (field: LoginFields) =>
    formik.touched[field] ? formik.errors[field] : '';

  return (
    <CustomLayout layoutType={layoutType}>
      <form onSubmit={formik.handleSubmit}>
        <VerticalStackLayout gap={5}>
          <FormControl label="Email" error={getFormikError('username')}>
            <Input
              data-testid="username"
              disabled={isLoginLoading}
              endEnhancer={
                <img
                  className="fill-current opacity-50"
                  src="/assets/img/icon/email.svg"
                  alt="email icon"
                />
              }
              error={getFormikError('username')}
              name="username"
              onBlur={formik.handleBlur}
              onChange={formik.handleChange}
              placeholder="Enter your email"
              value={formik.values.username}
            />
          </FormControl>
          <FormControl label="Password" error={getFormikError('password')}>
            <PasswordInput
              error={getFormikError('password')}
              name="password"
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              placeholder="Enter your password"
              value={formik.values.password}
            />
          </FormControl>
          <Flex alignItems="center" justifyContent="between">
            <label htmlFor="formCheckbox" className="flex cursor-pointer">
              <LoginFormCheckbox />
              <p>Remember me</p>
            </label>

            <Link
              to={routes.FORGOT_PASSWORD}
              className="text-sm text-primary hover:underline"
            >
              Forgot password?
            </Link>
          </Flex>
          <Button
            type={ButtonType.SUBMIT}
            kind={ButtonKind.PRIMARY}
            isLoading={isLoginLoading}
          >
            Log In
          </Button>
          <p className="self-center font-medium">
            Don’t have an account?{' '}
            <Link to={routes.SIGNUP} className="text-primary">
              Sign Up
            </Link>
          </p>
        </VerticalStackLayout>
      </form>
    </CustomLayout>
  );
};

export default LoginForm;
