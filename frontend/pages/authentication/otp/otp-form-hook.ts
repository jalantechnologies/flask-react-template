import { useFormik } from 'formik';
import * as Yup from 'yup';

import constant from 'frontend/constants';
import { useAuthContext } from 'frontend/contexts';
import { AsyncError, PhoneNumber } from 'frontend/types';

interface OTPFormProps {
  onError: (error: AsyncError) => void;
  onResendOTPSuccess: () => void;
  onVerifyOTPSuccess: () => void;
}

const useOTPForm = ({
  onError,
  onResendOTPSuccess,
  onVerifyOTPSuccess,
}: OTPFormProps) => {
  const {
    isVerifyOTPLoading,
    sendOTP,
    verifyOTP,
    verifyOTPError,
    verifyOTPResult,
  } = useAuthContext();

  const searchParams = new URLSearchParams(window.location.search);
  const phoneNumber = searchParams.get('phone_number');
  const countryCode = decodeURIComponent(
    searchParams.get('country_code') || '',
  );

  const formik = useFormik({
    initialValues: {
      otp: Array(constant.OTP_LENGTH).fill(''),
    },

    validationSchema: Yup.object({
      otp: Yup.array().of(Yup.string().required('')),
    }),

    onSubmit: (values) => {
      const otp = values.otp.join('');

      verifyOTP(
        new PhoneNumber({
          country_code: countryCode,
          phone_number: phoneNumber,
        }),
        otp,
      )
        .then(() => {
          onVerifyOTPSuccess();
        })
        .catch((error) => {
          onError(error as AsyncError);
        });
    },
  });

  const handleResendOTP = () => {
    sendOTP(
      new PhoneNumber({
        country_code: countryCode,
        phone_number: phoneNumber,
      }),
    )
      .then(() => {
        onResendOTPSuccess();
      })
      .catch((error) => {
        onError(error as AsyncError);
      });
  };

  return {
    countryCode,
    formik,
    handleResendOTP,
    isVerifyOTPLoading,
    phoneNumber,
    sendOTP,
    verifyOTPError,
    verifyOTPResult,
  };
};

export default useOTPForm;
