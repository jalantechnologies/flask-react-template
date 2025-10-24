import React, { useState } from 'react';

import Button from 'frontend/components/button';
import Input from 'frontend/components/input/';
import { ButtonKind } from 'frontend/types/button';

interface PasswordInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  name: string;
  placeholder: string;
  testId?: string;
}

const PasswordInput: React.FC<PasswordInputProps> = ({
  error,
  name,
  placeholder,
  testId,
  ...props
}) => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);

  const togglePasswordVisibility = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setIsPasswordVisible((prevState) => !prevState);
  };

  return (
    <Input
      data-testid="password"
      endEnhancer={
        <Button onClick={togglePasswordVisibility} kind={ButtonKind.SECONDARY}>
          {isPasswordVisible ? (
            <img
              className="size-6.5 opacity-65"
              src="/assets/img/icon/eye-closed.svg"
              alt="hide password icon"
            />
          ) : (
            <img
              className="size-6.5 opacity-65"
              src="/assets/img/icon/eye-open.svg"
              alt="show password icon"
            />
          )}
        </Button>
      }
      {...props}
      error={error}
      testId={testId}
      name={name}
      placeholder={placeholder}
      type={isPasswordVisible ? 'text' : 'password'}
    />
  );
};

export default PasswordInput;
