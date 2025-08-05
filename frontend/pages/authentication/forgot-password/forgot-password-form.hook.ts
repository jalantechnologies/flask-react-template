import { useFormik } from 'formik';
import * as Yup from 'yup';

import constant from 'frontend/constants';
import { useResetPasswordContext } from 'frontend/contexts';
import { AsyncError } from 'frontend/types';

interface UseForgotPasswordFormProps {
  onSuccess: (newUsername: string) => void;
  onError: (err: AsyncError) => void;
}

const useForgotPasswordForm = ({
  onError,
  onSuccess,
}: UseForgotPasswordFormProps) => {
  const {
    isSendForgotPasswordEmailLoading,
    sendForgotPasswordEmail,
    sendForgotPasswordEmailError,
  } = useResetPasswordContext();

  const formik = useFormik({
    initialValues: {
      username: '',
    },
    validationSchema: Yup.object({
      username: Yup.string()
        .email(constant.EMAIL_VALIDATION_ERROR)
        .required(constant.EMAIL_VALIDATION_ERROR),
    }),
    onSubmit: (values) => {
      sendForgotPasswordEmail(values.username)
        .then(() => {
          onSuccess(values.username);
        })
        .catch((err) => {
          onError(err as AsyncError);
        });
    },
  });

  return {
    isSendForgotPasswordEmailLoading,
    sendForgotPasswordEmailError,
    formik,
  };
};

export default useForgotPasswordForm;
