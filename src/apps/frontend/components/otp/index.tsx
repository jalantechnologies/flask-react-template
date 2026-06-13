import clsx from 'clsx';
import React, { FocusEventHandler, useRef } from 'react';

import CONTROL_CLASS from 'frontend/components/form-control/control-class';
import Inline from 'frontend/components/layout/inline';
import { KeyboardKeys } from 'frontend/types';
import { Spacing } from 'frontend/types/design-system';

interface OtpProps {
  // The current code as one string per digit box. Owned by the caller so the
  // form (Formik) stays the source of truth.
  value: string[];
  // Fires with the next full array of digit values on every keystroke.
  onChange: (values: string[]) => void;
  error?: string;
  disabled?: boolean;
  onBlur?: FocusEventHandler<HTMLInputElement>;
  testId?: string;
}

/**
 * A fixed-length numeric code input rendered as one box per digit. Typing a
 * digit advances focus; backspace moves to the previous box. Each box shares
 * the standard control surface, so the field looks like every other input and
 * pages never style it. The value/onChange contract is an array of digit
 * strings, one per box.
 */
const Otp: React.FC<OtpProps> = ({
  disabled = false,
  error,
  onBlur,
  onChange,
  testId,
  value,
}) => {
  const inputRefs = useRef<Array<HTMLInputElement | null>>([]);

  const handleDigitChange = (digit: string, index: number) => {
    // Keep only the last typed numeric character so a box never holds more
    // than one digit, matching the single-character box model.
    const sanitised = digit.replace(/\D/g, '').slice(-1);
    const next = [...value];
    next[index] = sanitised;
    onChange(next);

    if (sanitised && index < value.length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLInputElement>,
    index: number,
  ) => {
    if (
      event.key === KeyboardKeys.BACKSPACE.toString() &&
      !value[index] &&
      index > 0
    ) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  return (
    <Inline gap={Spacing.Sm} justify="center" testId={testId}>
      {value.map((digit, index) => (
        <input
          // The position is the stable identity for a fixed-length code; there
          // is no other key for an empty digit box.
          key={`otp-digit-${index}`}
          ref={(ref) => {
            inputRefs.current[index] = ref;
          }}
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={1}
          name="otp"
          value={digit}
          disabled={disabled}
          onChange={(event) => handleDigitChange(event.target.value, index)}
          onKeyDown={(event) => handleKeyDown(event, index)}
          onBlur={onBlur}
          aria-label={`Digit ${index + 1}`}
          aria-invalid={error ? true : undefined}
          className={clsx(
            CONTROL_CLASS,
            'w-12 text-center',
            error && 'border-danger focus:border-danger',
          )}
        />
      ))}
    </Inline>
  );
};

export default Otp;
