import React, { useState } from 'react';
import { Link } from 'react-router-dom';

import { AsyncError } from 'frontend//types';
import {
  Button,
  Checkbox,
  Inline,
  Spacing,
  Stack,
  Status,
  Text,
  TextField,
  Variant,
} from 'frontend/components';
import routes from 'frontend/constants/routes';
import useLoginForm from 'frontend/pages/login/login-form.hook';
import { ButtonType } from 'frontend/types/button';

type LoginFields = 'username' | 'password';

interface LoginFormProps {
  onSuccess: () => void;
  onError: (error: AsyncError) => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onError, onSuccess }) => {
  const { formik, isLoginLoading } = useLoginForm({ onSuccess, onError });
  const [rememberMe, setRememberMe] = useState(false);

  const getFormikError = (field: LoginFields) =>
    formik.touched[field] ? formik.errors[field] : '';

  return (
    <form onSubmit={formik.handleSubmit}>
      <Stack gap={Spacing.Md}>
        <TextField
          testId="username"
          label="Email"
          type="email"
          name="username"
          autoComplete="email"
          disabled={isLoginLoading}
          value={formik.values.username}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={getFormikError('username')}
          placeholder="Enter your email"
        />
        <TextField
          testId="password"
          label="Password"
          type="password"
          name="password"
          autoComplete="current-password"
          disabled={isLoginLoading}
          value={formik.values.password}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={getFormikError('password')}
          placeholder="Enter your password"
        />
        <Inline justify="between" align="center">
          <Checkbox
            checked={rememberMe}
            onCheckedChange={setRememberMe}
            label="Remember me"
          />
          <Link to={routes.FORGOT_PASSWORD}>
            <Text as="span" size="sm" variant={Status.Primary}>
              Forgot password?
            </Text>
          </Link>
        </Inline>
        <Button
          type={ButtonType.SUBMIT}
          variant={Variant.Primary}
          fullWidth
          isLoading={isLoginLoading}
        >
          Log In
        </Button>
        <Inline gap={Spacing.Xs} justify="center">
          <Text as="span" size="sm" weight="medium">
            Don&apos;t have an account?
          </Text>
          <Link to={routes.SIGNUP}>
            <Text as="span" size="sm" weight="medium" variant={Status.Primary}>
              Sign Up
            </Text>
          </Link>
        </Inline>
      </Stack>
    </form>
  );
};

export default LoginForm;
