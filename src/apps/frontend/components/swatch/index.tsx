import clsx from 'clsx';
import React from 'react';

interface SwatchProps {
  // A neutral placeholder tile used where a provider logo is unavailable.
  muted?: boolean;
  testId?: string;
}

/**
 * A small fixed-size rounded tile used as a logo placeholder. Encapsulates the
 * sized colored square so pages do not hand-write `size-8 rounded bg-gray-*`.
 */
const Swatch: React.FC<SwatchProps> = ({ muted = false, testId }) => (
  <span
    aria-hidden="true"
    data-testid={testId}
    className={clsx(
      'inline-flex size-8 items-center justify-center rounded',
      muted ? 'bg-surface-muted' : 'bg-line',
    )}
  >
    <span
      className={clsx(
        'size-3.5 rounded-sm',
        muted ? 'bg-line' : 'bg-line-strong',
      )}
    />
  </span>
);

export default Swatch;
