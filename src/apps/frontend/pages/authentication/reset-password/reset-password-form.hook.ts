import { useFormik } from 'formik';
import { useLocation, useParams } from 'react-router-dom';
import * as Yup from 'yup';

import constant from 'frontend/constants';
import { useResetPasswordContext } from 'frontend/contexts';
import { AsyncError } from 'frontend/types';
import { isPasswordStrongEnough } from 'frontend/utils/password-strength';

export type ResetPasswordParams = {
  accountId: string;
  newPassword: string;
  token: string;
};

interface ResetPasswordFormProps {
  onSuccess: () => void;
  onError: (err: AsyncError) => void;
}

const useResetPasswordForm = ({
  onError,
  onSuccess,
}: ResetPasswordFormProps) => {
  const { accountId } = useParams();

  const { search } = useLocation();
  const token = new URLSearchParams(search).get('token');

  const { isResetPasswordLoading, resetPasswordError, resetPassword } =
    useResetPasswordContext();

  const formik = useFormik({
    initialValues: {
      password: '',
      confirmPassword: '',
    },
    validationSchema: Yup.object({
      password: Yup.string()
        .min(
          constant.passwordPolicy.minLength,
          constant.passwordPolicy.lengthError,
        )
        .required(constant.passwordPolicy.lengthError)
        .test(
          'password-strength',
          constant.passwordPolicy.strengthError,
          (value) => isPasswordStrongEnough(value ?? ''),
        ),
      confirmPassword: Yup.string()
        .oneOf([Yup.ref('password')], constant.passwordPolicy.matchError)
        .required(constant.passwordPolicy.matchError),
    }),
    onSubmit: (values) => {
      resetPassword({
        accountId: accountId || '',
        newPassword: values.password,
        token: token || '',
      })
        .then(() => {
          onSuccess();
        })
        .catch((err) => {
          onError(err as AsyncError);
        });
    },
  });

  return {
    formik,
    isResetPasswordLoading,
    resetPasswordError,
  };
};

export default useResetPasswordForm;
