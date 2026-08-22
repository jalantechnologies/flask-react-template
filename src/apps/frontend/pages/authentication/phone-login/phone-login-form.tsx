import React from 'react';

import {
  Button,
  Inline,
  Select,
  Spacing,
  Stack,
  TextField,
  Variant,
} from 'frontend/components';
import COUNTRY_SELECT_OPTIONS from 'frontend/constants/countries';
import usePhoneLoginForm from 'frontend/pages/authentication/phone-login/phone-login-form.hook';
import { AsyncError } from 'frontend/types';
import { ButtonType } from 'frontend/types/button';

interface PhoneLoginFormProps {
  onSendOTPSuccess: () => void;
  onError: (error: AsyncError) => void;
}

const PhoneLoginForm: React.FC<PhoneLoginFormProps> = ({
  onError,
  onSendOTPSuccess,
}) => {
  const { formik, isSendOTPLoading } = usePhoneLoginForm({
    onSendOTPSuccess,
    onError,
  });

  const setFormikFieldValue = async (fieldName: string, data: string) => {
    try {
      await formik.setFieldValue(fieldName, data);
    } catch (err) {
      onError(err as AsyncError);
    }
  };

  const handleChangePhone = ({
    target,
  }: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = target;
    void setFormikFieldValue('phoneNumber', value);
  };

  const handleChangeSelect = ({
    target,
  }: React.ChangeEvent<HTMLSelectElement>) => {
    const { value } = target;
    const [countryCode, country] = value.split(', ');
    void setFormikFieldValue('country', country);
    void setFormikFieldValue('countryCode', countryCode);
    void setFormikFieldValue('phoneNumber', '');
  };

  return (
    <form onSubmit={formik.handleSubmit}>
      <Stack gap={Spacing.Md}>
        <Inline gap={Spacing.Sm} align="start">
          <Select
            label="Country"
            options={COUNTRY_SELECT_OPTIONS}
            disabled={isSendOTPLoading}
            value={`${formik.values.countryCode}, ${formik.values.country}`}
            onChange={handleChangeSelect}
            error={formik.touched.countryCode ? formik.errors.countryCode : ''}
          />
          <Stack flex>
            <TextField
              testId="phoneNumber"
              label="Phone number"
              type="number"
              name="phoneNumber"
              inputMode="numeric"
              disabled={isSendOTPLoading}
              value={formik.values.phoneNumber}
              onChange={handleChangePhone}
              onBlur={formik.handleBlur}
              error={
                formik.touched.phoneNumber ? formik.errors.phoneNumber : ''
              }
              placeholder="Enter your phone number"
            />
          </Stack>
        </Inline>
        <Button
          type={ButtonType.SUBMIT}
          isLoading={isSendOTPLoading}
          variant={Variant.Primary}
          fullWidth
        >
          Get OTP
        </Button>
      </Stack>
    </form>
  );
};

export default PhoneLoginForm;
