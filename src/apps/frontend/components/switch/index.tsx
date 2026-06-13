import clsx from 'clsx';
import React from 'react';

interface SwitchProps {
  checked: boolean;
  // Radix convention: fires with the next checked state.
  onCheckedChange: (checked: boolean) => void;
  // Accessible name. Required because the control has no visible text.
  ariaLabel: string;
  disabled?: boolean;
  testId?: string;
}

/**
 * An on/off toggle switch. Accessible (role=switch) with an animated knob,
 * following the Radix `checked` / `onCheckedChange` contract.
 */
const Switch: React.FC<SwitchProps> = ({
  ariaLabel,
  checked,
  disabled = false,
  onCheckedChange,
  testId,
}) => (
  <button
    type="button"
    role="switch"
    aria-checked={checked}
    aria-label={ariaLabel}
    disabled={disabled}
    data-testid={testId}
    onClick={() => onCheckedChange(!checked)}
    className={clsx(
      'relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors disabled:cursor-not-allowed disabled:opacity-50',
      checked ? 'bg-primary' : 'bg-line-strong',
    )}
  >
    <span
      className={clsx(
        'inline-block size-5 rounded-full bg-surface transition-transform',
        checked ? 'translate-x-5' : 'translate-x-0.5',
      )}
    />
  </button>
);

export default Switch;
