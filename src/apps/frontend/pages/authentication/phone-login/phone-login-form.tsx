import React from 'react';

import {
  Button,
  Flex,
  FormControl,
  Input,
  Select,
  VerticalStackLayout,
} from 'frontend/components';
import COUNTRY_SELECT_OPTIONS from 'frontend/constants/countries';
import usePhoneLoginForm from 'frontend/pages/authentication/phone-login/phone-login-form.hook';
import { AsyncError } from 'frontend/types';
import { ButtonKind, ButtonType } from 'frontend/types/button';

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

  const setFormikFieldValue = (fieldName: string, data: string) => {
    formik
      .setFieldValue(fieldName, data)
      .then()
      .catch((err) => {
        onError(err as AsyncError);
      });
  };

  const handleChangePhone = ({
    target,
  }: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = target;
    setFormikFieldValue('phoneNumber', value);
  };

  const handleChangeSelect = ({
    target,
  }: React.ChangeEvent<HTMLSelectElement>) => {
    const { value } = target;
    const [countryCode, country] = value.split(', ');
    setFormikFieldValue('country', country);
    setFormikFieldValue('countryCode', countryCode);
    setFormikFieldValue('phoneNumber', '');
  };

  return (
    <form onSubmit={formik.handleSubmit}>
      <VerticalStackLayout gap={5}>
        <Flex gap={4}>
          <FormControl
            label={'Phone'}
            error={formik.touched.countryCode ? formik.errors.countryCode : ''}
          >
            <Select
              handleChange={handleChangeSelect}
              isLoading={isSendOTPLoading}
              options={COUNTRY_SELECT_OPTIONS}
              value={`${formik.values.countryCode}, ${formik.values.country}`}
            />
          </FormControl>
          <div className="w-full">
            <FormControl
              label={''}
              error={
                formik.touched.phoneNumber ? formik.errors.phoneNumber : ''
              }
            >
              <Input
                data-testid="phoneNumber"
                disabled={isSendOTPLoading}
                error={
                  formik.touched.phoneNumber ? formik.errors.phoneNumber : ''
                }
                name="phoneNumber"
                onChange={handleChangePhone}
                onBlur={formik.handleBlur}
                placeholder="Enter your phone number"
                type="number"
                value={formik.values.phoneNumber}
              />
            </FormControl>
          </div>
        </Flex>

        <Button
          type={ButtonType.SUBMIT}
          isLoading={isSendOTPLoading}
          kind={ButtonKind.PRIMARY}
        >
          Get OTP
        </Button>
      </VerticalStackLayout>
    </form>
  );
};

export default PhoneLoginForm;
