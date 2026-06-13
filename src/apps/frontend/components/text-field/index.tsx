import clsx from 'clsx';
import React from 'react';

import Field from 'frontend/components/field';
import CONTROL_CLASS from 'frontend/components/form-control/control-class';
import { describedBy } from 'frontend/components/form-control/described-by';

interface TextFieldProps {
  value: string;
  // Receives the native change event, matching the DOM and shadcn input.
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  label?: string;
  hint?: string;
  error?: string;
  type?: 'text' | 'email' | 'url' | 'password' | 'number' | 'date';
  placeholder?: string;
  id?: string;
  name?: string;
  required?: boolean;
  disabled?: boolean;
  autoFocus?: boolean;
  monospace?: boolean;
  // Native input affordances for constrained entry (e.g. numeric OTP codes).
  inputMode?: 'text' | 'numeric' | 'decimal' | 'tel' | 'email' | 'url';
  pattern?: string;
  maxLength?: number;
  textAlign?: 'left' | 'center' | 'right';
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  testId?: string;
  // Accessible name when there is no visible `label`.
  ariaLabel?: string;
  // Native autocomplete hint. Defaults to 'off'; credential forms should set
  // 'email' / 'current-password' / etc. so browsers and password managers work.
  autoComplete?: string;
}

const ALIGN_CLASS: Record<NonNullable<TextFieldProps['textAlign']>, string> = {
  left: 'text-left',
  center: 'text-center',
  right: 'text-right',
};

/**
 * A labelled single-line text input. The canonical way to collect text on a
 * form: pages set value/onChange and a label, never the input styling.
 */
const TextField: React.FC<TextFieldProps> = ({
  ariaLabel,
  autoComplete = 'off',
  autoFocus,
  disabled,
  error,
  hint,
  id,
  inputMode,
  label,
  maxLength,
  monospace,
  name,
  onBlur,
  onChange,
  pattern,
  placeholder,
  required,
  testId,
  textAlign = 'left',
  type = 'text',
  value,
}) => {
  const generatedId = React.useId();
  const inputId = id ?? generatedId;
  return (
    <Field label={label} hint={hint} error={error} htmlFor={inputId}>
      <input
        id={inputId}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        autoFocus={autoFocus}
        autoComplete={autoComplete}
        inputMode={inputMode}
        pattern={pattern}
        maxLength={maxLength}
        aria-label={label ? undefined : ariaLabel}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(inputId, {
          error: Boolean(error),
          hint: Boolean(hint),
        })}
        data-testid={testId}
        className={clsx(
          CONTROL_CLASS,
          ALIGN_CLASS[textAlign],
          error && 'border-danger focus:border-danger',
          monospace && 'font-mono',
        )}
      />
    </Field>
  );
};

export default TextField;
