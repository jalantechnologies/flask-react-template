import clsx from 'clsx';
import React from 'react';

import Field from 'frontend/components/field';
import CONTROL_CLASS from 'frontend/components/form-control/control-class';
import { describedBy } from 'frontend/components/form-control/described-by';

interface TextareaProps {
  value: string;
  // Receives the native change event, matching the DOM and shadcn textarea.
  onChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
  label?: string;
  hint?: string;
  error?: string;
  placeholder?: string;
  id?: string;
  rows?: number;
  required?: boolean;
  disabled?: boolean;
  monospace?: boolean;
  autoFocus?: boolean;
  // Cap growth at half the viewport for long editors.
  capHeight?: boolean;
  testId?: string;
  ariaLabel?: string;
}

/** A labelled multi-line text input sharing the standard control surface. */
const Textarea: React.FC<TextareaProps> = ({
  ariaLabel,
  autoFocus,
  capHeight = false,
  disabled,
  error,
  hint,
  id,
  label,
  monospace,
  onChange,
  placeholder,
  required,
  rows = 4,
  testId,
  value,
}) => {
  const generatedId = React.useId();
  const textareaId = id ?? generatedId;
  return (
    <Field label={label} hint={hint} error={error} htmlFor={textareaId}>
      <textarea
        id={textareaId}
        rows={rows}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        autoFocus={autoFocus}
        aria-label={label ? undefined : ariaLabel}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(textareaId, {
          error: Boolean(error),
          hint: Boolean(hint),
        })}
        data-testid={testId}
        className={clsx(
          CONTROL_CLASS,
          'resize-y',
          capHeight && 'max-h-[50vh]',
          error && 'border-danger focus:border-danger',
          monospace && 'font-mono',
        )}
      />
    </Field>
  );
};

export default Textarea;
