import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import {
  Button,
  Flex,
  FormControl,
  OTP,
  VerticalStackLayout,
} from 'frontend/components';
import OtpHint from 'frontend/components/otp/otp-hint';
import routes from 'frontend/constants/routes';
import { Config } from 'frontend/helpers';
import useOTPForm from 'frontend/pages/authentication/otp/otp-form-hook';
import { AsyncError } from 'frontend/types';
import { ButtonKind, ButtonType } from 'frontend/types/button';

interface OTPFormProps {
  isResendEnabled: boolean;
  onError: (error: AsyncError) => void;
  onResendOTPSuccess: () => void;
  onVerifyOTPSuccess: () => void;
  timerRemainingSeconds: string;
}

const defaultOTPConfig = Config.getConfigValue<{
  code: string;
  enabled: boolean;
}>('default_otp');
const isOTPEnabled = defaultOTPConfig?.enabled;
const defaultOTPCode = defaultOTPConfig?.code;

const OTPForm: React.FC<OTPFormProps> = ({
  isResendEnabled,
  onError,
  onResendOTPSuccess,
  onVerifyOTPSuccess,
  timerRemainingSeconds,
}) => {
  const {
    countryCode,
    formik,
    phoneNumber,
    isVerifyOTPLoading,
    handleResendOTP,
  } = useOTPForm({
    onError,
    onResendOTPSuccess,
    onVerifyOTPSuccess,
  });

  const navigate = useNavigate();

  useEffect(() => {
    if (!phoneNumber || !countryCode) {
      navigate(routes.LOGIN);
    }
  }, [phoneNumber, countryCode, navigate]);

  const handleChange = (value: string[]) => {
    formik
      .setFieldValue('otp', value)
      .then()
      .catch((error) => {
        onError(error as AsyncError);
      });
  };

  return (
    <form onSubmit={formik.handleSubmit}>
      <VerticalStackLayout gap={5}>
        <FormControl
          label={`Enter the 4 digit code sent to the mobile number ${countryCode} ${phoneNumber}`}
          error={formik.touched.otp ? (formik.errors.otp as string) : ''}
        >
          <OTP
            error={formik.touched.otp ? (formik.errors.otp as string) : ''}
            isLoading={isVerifyOTPLoading}
            onError={onError}
            onBlur={formik.handleBlur}
            onChange={handleChange}
          />
        </FormControl>
        {isOTPEnabled && <OtpHint otpCode={defaultOTPCode} />}
        <Flex gap={2}>
          <p className="text-lg text-black">Did not receive a code?</p>
          <Button
            disabled={!isResendEnabled}
            kind={ButtonKind.TERTIARY}
            onClick={handleResendOTP}
          >
            {isResendEnabled
              ? 'Resend'
              : `Resend OTP in 00: ${timerRemainingSeconds}`}
          </Button>
        </Flex>

        <Button
          type={ButtonType.SUBMIT}
          isLoading={isVerifyOTPLoading}
          kind={ButtonKind.PRIMARY}
        >
          Verify
        </Button>
      </VerticalStackLayout>
    </form>
  );
};

export default OTPForm;
