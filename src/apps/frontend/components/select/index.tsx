import clsx from 'clsx';
import React from 'react';

import Field from 'frontend/components/field';
import CONTROL_CLASS from 'frontend/components/form-control/control-class';
import { describedBy } from 'frontend/components/form-control/described-by';

export interface SelectOption {
  label: string;
  value: string;
}

interface SelectProps {
  value: string;
  options: SelectOption[];
  // Receives the native change event, matching the DOM and shadcn select.
  onChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  label?: string;
  hint?: string;
  error?: string;
  id?: string;
  disabled?: boolean;
  placeholder?: string;
  testId?: string;
  ariaLabel?: string;
}

/**
 * A labelled dropdown sharing the standard control surface. Pages pass typed
 * options and a value; they never style the native select.
 */
const Select: React.FC<SelectProps> = ({
  ariaLabel,
  disabled,
  error,
  hint,
  id,
  label,
  onChange,
  options,
  placeholder,
  testId,
  value,
}) => {
  const generatedId = React.useId();
  const selectId = id ?? generatedId;
  return (
    <Field label={label} hint={hint} error={error} htmlFor={selectId}>
      <select
        id={selectId}
        value={value}
        disabled={disabled}
        onChange={onChange}
        aria-label={label ? undefined : ariaLabel}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(selectId, {
          error: Boolean(error),
          hint: Boolean(hint),
        })}
        data-testid={testId}
        className={clsx(
          CONTROL_CLASS,
          error && 'border-danger focus:border-danger',
        )}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </Field>
  );
};

export default Select;
