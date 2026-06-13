import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

import { Status } from 'frontend/types/design-system';

interface AlertProps {
  // Status colour, following the shadcn/Bootstrap `variant` convention.
  variant?: Status;
  // When true, renders as a full-bleed band (used inside page bodies for
  // inline errors) rather than a rounded standalone notice.
  band?: boolean;
  testId?: string;
}

// Danger and warning alerts announce assertively; the rest are polite.
const ALERT_ROLE: Partial<Record<Status, 'alert' | 'status'>> = {
  [Status.Danger]: 'alert',
  [Status.Warning]: 'alert',
};

const VARIANT_CLASS: Record<Status, string> = {
  [Status.Neutral]: 'bg-surface-muted text-content-subtle',
  [Status.Primary]: 'bg-primary/5 text-content',
  [Status.Success]: 'bg-success-soft text-success-softText',
  [Status.Danger]: 'bg-danger-soft text-danger-softText',
  [Status.Warning]: 'bg-warning-soft text-warning-softText',
  [Status.Info]: 'bg-info-soft text-info-softText',
  [Status.Accent]: 'bg-accent-soft text-accent-softText',
};

/**
 * An inline message surface for errors, warnings, and notices. Variant-driven,
 * replacing the assorted `bg-red-50 text-red-600` snippets across pages.
 */
const Alert: React.FC<PropsWithChildren<AlertProps>> = ({
  band = false,
  children,
  testId,
  variant = Status.Danger,
}) => (
  <div
    role={ALERT_ROLE[variant] ?? 'status'}
    data-testid={testId}
    className={clsx(
      'text-xs',
      VARIANT_CLASS[variant],
      band ? 'px-6 py-2' : 'rounded-md px-3 py-2',
    )}
  >
    {children}
  </div>
);

export { Status } from 'frontend/types/design-system';
export default Alert;
