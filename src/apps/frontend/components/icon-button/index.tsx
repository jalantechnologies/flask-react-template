import clsx from 'clsx';
import React from 'react';

import { ButtonType } from 'frontend/types/button';
import { Size, Status } from 'frontend/types/design-system';

interface IconButtonProps {
  // An accessible label is required: icon buttons have no visible text.
  label: string;
  icon: React.ReactNode;
  variant?: Status;
  size?: Size;
  disabled?: boolean;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  type?: ButtonType;
  testId?: string;
  // When the button toggles a disclosure (popover, menu), wire the open state
  // and the controlled region so assistive tech announces the relationship.
  expanded?: boolean;
  controls?: string;
}

const BASE =
  'inline-flex items-center justify-center rounded transition-colors disabled:cursor-not-allowed disabled:opacity-40';

const VARIANT_CLASS: Record<Status, string> = {
  [Status.Neutral]:
    'text-content-muted hover:bg-surface-muted hover:text-content-subtle',
  [Status.Primary]: 'text-primary hover:bg-surface-muted',
  [Status.Success]: 'text-success hover:bg-success-soft',
  [Status.Danger]: 'text-danger hover:bg-danger-soft',
  [Status.Warning]: 'text-warning hover:bg-warning-soft',
  [Status.Info]: 'text-info hover:bg-info-soft',
  [Status.Accent]: 'text-accent hover:bg-accent-soft',
};

const SIZE_CLASS: Record<Size, string> = {
  [Size.Sm]: 'p-1',
  [Size.Md]: 'p-1.5',
  [Size.Lg]: 'p-2',
};

/**
 * A compact, icon-only action. Used for row actions and toolbar controls
 * instead of bare `<button>` elements with hand-written hover classes.
 *
 * Forwards its ref to the underlying `<button>` so callers can anchor a
 * popover to it or restore focus to it (e.g. a disclosure trigger).
 */
const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      controls,
      disabled = false,
      expanded,
      icon,
      label,
      onClick,
      size = Size.Md,
      testId,
      type = ButtonType.BUTTON,
      variant = Status.Neutral,
    },
    ref,
  ) => (
    <button
      ref={ref}
      aria-label={label}
      title={label}
      aria-expanded={expanded}
      aria-controls={controls}
      type={type}
      disabled={disabled}
      onClick={onClick}
      data-testid={testId}
      className={clsx(BASE, VARIANT_CLASS[variant], SIZE_CLASS[size])}
    >
      {icon}
    </button>
  ),
);

IconButton.displayName = 'IconButton';

export default IconButton;
