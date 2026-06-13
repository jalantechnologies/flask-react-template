import React from 'react';

import Text, { Emphasis } from 'frontend/components/typography/text';

interface CheckboxProps {
  checked: boolean;
  // Radix convention: fires with the next checked state.
  onCheckedChange: (checked: boolean) => void;
  // Optional visible label. When omitted, supply an accessible name via
  // ariaLabel for a standalone checkbox.
  label?: string;
  ariaLabel?: string;
  disabled?: boolean;
  testId?: string;
}

const CONTROL_CLASS =
  'size-4 rounded border-line-strong accent-primary focus:ring-0';

/**
 * A checkbox following the Radix `checked` / `onCheckedChange` contract.
 * Renders a labelled row when `label` is given, or a bare control otherwise.
 */
const Checkbox: React.FC<CheckboxProps> = ({
  ariaLabel,
  checked,
  disabled = false,
  label,
  onCheckedChange,
  testId,
}) => {
  const input = (
    <input
      type="checkbox"
      checked={checked}
      disabled={disabled}
      aria-label={label ? undefined : ariaLabel}
      data-testid={testId}
      onChange={(e) => onCheckedChange(e.target.checked)}
      className={CONTROL_CLASS}
    />
  );

  if (!label) {
    return input;
  }

  return (
    <label className="flex cursor-pointer items-center gap-2">
      {input}
      <Text as="span" size="sm" emphasis={Emphasis.Subtle}>
        {label}
      </Text>
    </label>
  );
};

export default Checkbox;
