import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

import { Status } from 'frontend/types/design-system';

interface BadgeProps {
  // Status colour, following the shadcn/Bootstrap `variant` convention.
  variant?: Status;
  testId?: string;
}

const VARIANT_CLASS: Record<Status, string> = {
  [Status.Neutral]: 'bg-surface-muted text-content-subtle',
  [Status.Primary]: 'bg-primary text-content-inverted',
  [Status.Success]: 'bg-success-soft text-success-softText',
  [Status.Danger]: 'bg-danger-soft text-danger-softText',
  [Status.Warning]: 'bg-warning-soft text-warning-softText',
  [Status.Info]: 'bg-info-soft text-info-softText',
  [Status.Accent]: 'bg-accent-soft text-accent-softText',
};

/**
 * A pill label for status, role, and category. One component, many variants,
 * replacing the per-page RoleBadge / LoginBadge / SourceBadge variants.
 */
const Badge: React.FC<PropsWithChildren<BadgeProps>> = ({
  children,
  testId,
  variant = Status.Neutral,
}) => (
  <span
    data-testid={testId}
    className={clsx(
      'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium',
      VARIANT_CLASS[variant],
    )}
  >
    {children}
  </span>
);

export { Status } from 'frontend/types/design-system';
export default Badge;
