import React, { useRef, useState, FocusEventHandler } from 'react';

import OTPInput from 'frontend/components/otp/otp-input';
import constant from 'frontend/constants';
import { AsyncError, KeyboardKeys } from 'frontend/types';

interface OTPProps {
  error?: string;
  isLoading: boolean;
  onBlur?: FocusEventHandler<HTMLInputElement>;
  onChange: (values: string[]) => void;
  onError: (error: AsyncError) => void;
}

const OTP: React.FC<OTPProps> = ({ error, isLoading, onBlur, onChange }) => {
  const [otp, setOTP] = useState<string[]>(Array(constant.OTP_LENGTH).fill(''));

  const inputRef = useRef<HTMLInputElement[]>([]);

  const handleInputRef = (ref: HTMLInputElement) => {
    inputRef.current.push(ref);
  };

  const handleOTPChange = (inputValue: string, index: number): void => {
    const otpInputs = [...otp];

    if (inputValue.length >= constant.OTP_INPUT_MAX_LENGTH) return;

    otpInputs[index] = inputValue;
    setOTP(otpInputs);

    if (inputValue.length === 1 && index < constant.OTP_LENGTH - 1) {
      inputRef.current[index + 1]?.focus();
    }

    if (inputValue.length === 0 && index > 0) {
      inputRef.current[index - 1]?.focus();
    }

    onChange(otpInputs);
  };

  const handleOnKeyDown = (
    { key }: React.KeyboardEvent<HTMLInputElement>,
    index: number,
  ) => {
    if (key === KeyboardKeys.BACKSPACE.toString()) {
      inputRef.current[index - 1]?.focus();
    }
  };

  return (
    <div className="flex justify-center gap-3">
      {otp.map((_, index) => (
        <div key={index} className="flex-1">
          <OTPInput
            disabled={isLoading}
            index={index}
            name={'otp'}
            error={error || ''}
            onChange={(e) => handleOTPChange(e.target.value, index)}
            onBlur={onBlur}
            onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) =>
              handleOnKeyDown(e, index + 1)
            }
            handleInputRef={handleInputRef}
            value={otp[index]}
          />
        </div>
      ))}
    </div>
  );
};

export default OTP;
