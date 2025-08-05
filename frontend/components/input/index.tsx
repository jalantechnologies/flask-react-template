import clsx from 'clsx';
import * as React from 'react';

import HorizontalStackLayout from 'frontend/components/layouts/horizontal-stack-layout';
import { Nullable } from 'frontend/types/common-types';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  endEnhancer?: React.ReactElement | string;
  error?: string;
  handleInputRef?: (ref: Nullable<HTMLInputElement>) => void;
  index?: number;
  startEnhancer?: React.ReactElement | string;
  testId?: string;
  textAlign?: 'left' | 'center' | 'right';
  type?: string;
}

const Input: React.FC<InputProps> = ({
  endEnhancer,
  error,
  handleInputRef,
  index,
  startEnhancer,
  testId,
  textAlign = 'left',
  type,
  ...props
}) => (
  <div
    className={clsx(
      'w-full rounded-lg border bg-white p-4 outline-none focus:border-primary focus-visible:shadow-none',
      error ? 'border-red-500' : 'border-stroke',
    )}
  >
    <HorizontalStackLayout gap={2}>
      {startEnhancer && (
        <span className="flex h-full min-w-6 items-center justify-center">
          {startEnhancer}
        </span>
      )}
      <input
        {...props}
        autoComplete="off"
        className={clsx(
          'w-full flex-1 appearance-none outline-none',
          '[&::-webkit-inner-spin-button]:appearance-none',
          textAlign === 'left' && 'text-left',
          textAlign === 'center' && 'text-center',
          textAlign === 'right' && 'text-right',
        )}
        data-testid={testId}
        type={type || 'text'}
        ref={handleInputRef ? (ref) => handleInputRef(ref) : null}
      />
      {endEnhancer && (
        <span className="flex h-full min-w-6 items-center justify-center">
          {endEnhancer}
        </span>
      )}
    </HorizontalStackLayout>
  </div>
);

export default Input;
