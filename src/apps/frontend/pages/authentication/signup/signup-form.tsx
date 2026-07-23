import React from 'react';
import { Link } from 'react-router-dom';

import {
  Button,
  Inline,
  PasswordStrengthMeter,
  Spacing,
  Stack,
  Status,
  Text,
  TextField,
  Variant,
} from 'frontend/components';
import routes from 'frontend/constants/routes';
import useSignupForm from 'frontend/pages/authentication/signup/signup-form.hook';
import { AsyncError } from 'frontend/types';
import { ButtonType } from 'frontend/types/button';
import { getPasswordMinScore } from 'frontend/utils/password-strength';

type SignupFields =
  | 'firstName'
  | 'lastName'
  | 'username'
  | 'password'
  | 'retypePassword';

interface SignupFormProps {
  onError: (error: AsyncError) => void;
  onSuccess: () => void;
}

const SignupForm: React.FC<SignupFormProps> = ({ onError, onSuccess }) => {
  const { formik, isSignupLoading } = useSignupForm({ onSuccess, onError });

  const getFormikError = (field: SignupFields) =>
    formik.touched[field] ? formik.errors[field] : '';

  return (
    <form onSubmit={formik.handleSubmit}>
      <Stack gap={Spacing.Md}>
        <Inline gap={Spacing.Md} align="start">
          <Stack flex>
            <TextField
              testId="firstName"
              label="First name"
              name="firstName"
              disabled={isSignupLoading}
              value={formik.values.firstName}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={getFormikError('firstName')}
              placeholder="Enter your first name"
            />
          </Stack>
          <Stack flex>
            <TextField
              testId="lastName"
              label="Last name"
              name="lastName"
              disabled={isSignupLoading}
              value={formik.values.lastName}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={getFormikError('lastName')}
              placeholder="Enter your last name"
            />
          </Stack>
        </Inline>
        <TextField
          testId="username"
          label="Email"
          type="email"
          name="username"
          autoComplete="email"
          disabled={isSignupLoading}
          value={formik.values.username}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={getFormikError('username')}
          placeholder="Enter your email"
        />
        <Stack gap={Spacing.Xs}>
          <TextField
            testId="password"
            label="Password"
            type="password"
            name="password"
            autoComplete="new-password"
            disabled={isSignupLoading}
            value={formik.values.password}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={getFormikError('password')}
            placeholder="Enter your password"
          />
          <PasswordStrengthMeter
            testId="password-strength"
            password={formik.values.password}
            minScore={getPasswordMinScore()}
          />
        </Stack>
        <TextField
          testId="retypePassword"
          label="Re-type Password"
          type="password"
          name="retypePassword"
          autoComplete="new-password"
          disabled={isSignupLoading}
          value={formik.values.retypePassword}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={getFormikError('retypePassword')}
          placeholder="Re-enter the password"
        />
        <Button
          type={ButtonType.SUBMIT}
          variant={Variant.Primary}
          fullWidth
          isLoading={isSignupLoading}
        >
          Sign Up
        </Button>
        <Inline gap={Spacing.Xs} justify="center">
          <Text as="span" size="sm" weight="medium">
            Already have an account?
          </Text>
          <Link to={routes.LOGIN}>
            <Text as="span" size="sm" weight="medium" variant={Status.Primary}>
              Log in
            </Text>
          </Link>
        </Inline>
      </Stack>
    </form>
  );
};

export default SignupForm;
