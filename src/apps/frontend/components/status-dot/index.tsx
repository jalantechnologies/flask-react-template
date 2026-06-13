import clsx from 'clsx';
import React from 'react';

import { Status } from 'frontend/types/design-system';

interface StatusDotProps {
  variant?: Status;
  // Widens the dot into a pill. Used to mark the active item in a sequence
  // (e.g. a step tracker) so the current position reads by shape, not colour
  // alone — important for colour-blind users.
  wide?: boolean;
  // An accessible name when the dot conveys meaning on its own (not paired
  // with adjacent text). Rendered as visually-hidden text so the dot itself
  // stays decorative rather than relying on an img role on a styled element.
  ariaLabel?: string;
  testId?: string;
}

const VARIANT_CLASS: Record<Status, string> = {
  [Status.Neutral]: 'bg-content-faint',
  [Status.Primary]: 'bg-primary',
  [Status.Success]: 'bg-success',
  [Status.Danger]: 'bg-danger',
  [Status.Warning]: 'bg-warning',
  [Status.Info]: 'bg-info',
  [Status.Accent]: 'bg-accent',
};

/** A small filled pill indicating live status, tinted by variant. */
const StatusDot: React.FC<StatusDotProps> = ({
  ariaLabel,
  testId,
  variant = Status.Neutral,
  wide = false,
}) => (
  <>
    <span
      aria-hidden="true"
      data-testid={testId}
      className={clsx(
        'inline-block h-2 rounded-full transition-all',
        wide ? 'w-5' : 'w-2',
        VARIANT_CLASS[variant],
      )}
    />
    {ariaLabel && <span className="sr-only">{ariaLabel}</span>}
  </>
);

export default StatusDot;
