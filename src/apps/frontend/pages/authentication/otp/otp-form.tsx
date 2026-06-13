import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import {
  Button,
  Field,
  Inline,
  Otp,
  Spacing,
  Stack,
  Text,
  Variant,
} from 'frontend/components';
import routes from 'frontend/constants/routes';
import { Config } from 'frontend/helpers';
import useOTPForm from 'frontend/pages/authentication/otp/otp-form-hook';
import OtpHint from 'frontend/pages/authentication/otp/otp-hint';
import { AsyncError } from 'frontend/types';
import { ButtonType } from 'frontend/types/button';

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

  const otpError = formik.touched.otp ? (formik.errors.otp as string) : '';

  return (
    <form onSubmit={formik.handleSubmit}>
      <Stack gap={Spacing.Md}>
        <Field
          label={`Enter the 4 digit code sent to the mobile number ${countryCode} ${phoneNumber}`}
          error={otpError}
        >
          <Otp
            value={formik.values.otp as string[]}
            disabled={isVerifyOTPLoading}
            error={otpError}
            onBlur={formik.handleBlur}
            onChange={handleChange}
          />
        </Field>
        {isOTPEnabled && <OtpHint otpCode={defaultOTPCode} />}
        <Inline gap={Spacing.Xs} align="center">
          <Text as="span" size="sm">
            Did not receive a code?
          </Text>
          <Button
            disabled={!isResendEnabled}
            variant={Variant.Tertiary}
            onClick={handleResendOTP}
          >
            {isResendEnabled
              ? 'Resend'
              : `Resend OTP in 00: ${timerRemainingSeconds}`}
          </Button>
        </Inline>
        <Button
          type={ButtonType.SUBMIT}
          isLoading={isVerifyOTPLoading}
          variant={Variant.Primary}
          fullWidth
        >
          Verify
        </Button>
      </Stack>
    </form>
  );
};

export default OTPForm;
