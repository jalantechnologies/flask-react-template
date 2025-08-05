import React from 'react';
import { Link } from 'react-router-dom';

import {
  Button,
  Flex,
  FormControl,
  Input,
  PasswordInput,
  VerticalStackLayout,
} from 'frontend/components';
import { CustomLayout } from 'frontend/components/layouts/custom-layout.component';
import { LayoutType } from 'frontend/components/layouts/layout-config';
import routes from 'frontend/constants/routes';
import useSignupForm from 'frontend/pages/authentication/signup/signup-form.hook';
import { AsyncError } from 'frontend/types';
import { ButtonKind, ButtonType } from 'frontend/types/button';

type SignupFields =
  | 'firstName'
  | 'lastName'
  | 'username'
  | 'password'
  | 'retypePassword';

interface SignupFormProps {
  onError: (error: AsyncError) => void;
  onSuccess: () => void;
  layoutType?: LayoutType;
}

const SignupForm: React.FC<SignupFormProps> = ({
  onError,
  onSuccess,
  layoutType = LayoutType.Default,
}) => {
  const { formik, isSignupLoading } = useSignupForm({ onSuccess, onError });

  const getFormikError = (field: SignupFields) =>
    formik.touched[field] ? formik.errors[field] : '';

  return (
    <CustomLayout layoutType={layoutType}>
      <form onSubmit={formik.handleSubmit}>
        <VerticalStackLayout gap={5}>
          <Flex gap={6}>
            <div className="w-full">
              <FormControl
                label="First name"
                error={getFormikError('firstName')}
              >
                <Input
                  error={getFormikError('firstName')}
                  data-testid="firstName"
                  disabled={isSignupLoading}
                  name="firstName"
                  onBlur={formik.handleBlur}
                  onChange={formik.handleChange}
                  placeholder="Enter your first name"
                  value={formik.values.firstName}
                />
              </FormControl>
            </div>
            <div className="w-full">
              <FormControl label="Last name" error={getFormikError('lastName')}>
                <Input
                  error={getFormikError('lastName')}
                  data-testid="lastName"
                  disabled={isSignupLoading}
                  name="lastName"
                  onBlur={formik.handleBlur}
                  onChange={formik.handleChange}
                  placeholder="Enter your last name"
                  value={formik.values.lastName}
                />
              </FormControl>
            </div>
          </Flex>
          <FormControl label="Email" error={getFormikError('username')}>
            <Input
              data-testid="username"
              disabled={isSignupLoading}
              endEnhancer={
                <img
                  alt="email icon"
                  className="fill-current opacity-50"
                  src="/assets/img/icon/email.svg"
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
              onBlur={formik.handleBlur}
              onChange={formik.handleChange}
              placeholder="Enter your password"
              value={formik.values.password}
            />
          </FormControl>
          <FormControl
            label="Re-type Password"
            error={getFormikError('retypePassword')}
          >
            <PasswordInput
              error={getFormikError('retypePassword')}
              name="retypePassword"
              onBlur={formik.handleBlur}
              onChange={formik.handleChange}
              placeholder="Re-enter the password"
              value={formik.values.retypePassword}
            />
          </FormControl>
          <Button
            type={ButtonType.SUBMIT}
            kind={ButtonKind.PRIMARY}
            isLoading={isSignupLoading}
          >
            Sign Up
          </Button>
          <p className="self-center font-medium">
            Already have an account?{' '}
            <Link to={routes.LOGIN} className="text-primary">
              Log in
            </Link>
          </p>
        </VerticalStackLayout>
      </form>
    </CustomLayout>
  );
};

export default SignupForm;
