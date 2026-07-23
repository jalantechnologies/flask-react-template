import { useFormik } from 'formik';
import * as Yup from 'yup';

import constant from 'frontend/constants';
import { useAuthContext } from 'frontend/contexts';
import { AsyncError } from 'frontend/types';

interface LoginFormProps {
  onSuccess: () => void;
  onError: (error: AsyncError) => void;
}
const useLoginForm = ({ onError, onSuccess }: LoginFormProps) => {
  const { isLoginLoading, login, loginError, loginResult } = useAuthContext();

  const formik = useFormik({
    initialValues: {
      username: '',
      password: '',
    },
    validationSchema: Yup.object({
      username: Yup.string()
        .email(constant.EMAIL_VALIDATION_ERROR)
        .required(constant.EMAIL_VALIDATION_ERROR),
      password: Yup.string()
        .min(
          constant.passwordPolicy.minLength,
          constant.passwordPolicy.lengthError,
        )
        .required(constant.passwordPolicy.lengthError),
    }),
    onSubmit: (values) => {
      login(values.username, values.password)
        .then(() => {
          onSuccess();
        })
        .catch((error) => {
          onError(error as AsyncError);
        });
    },
  });

  return {
    isLoginLoading,
    loginError,
    loginResult,
    formik,
  };
};

export default useLoginForm;
