import clsx from 'clsx';
import React from 'react';

import {
  ICON_ROTATE_CLASS,
  ICON_SIZE_CLASS,
  ICON_TONE_CLASS,
  IconRotate,
  IconSize,
  IconTone,
} from 'frontend/components/icons/icon-tokens';

// Token props shared by every icon. Each concrete icon spreads these onto
// IconBase and supplies only its own viewBox/fill/paths.
export interface IconProps {
  size?: IconSize;
  tone?: IconTone;
  rotate?: IconRotate;
  // Animates rotation changes, for a glyph that flips on an interaction
  // (e.g. a disclosure chevron).
  transition?: boolean;
  // Dims the glyph (e.g. a de-emphasised brand mark).
  muted?: boolean;
  testId?: string;
  // When set, the glyph is meaningful: it drops aria-hidden and exposes an
  // accessible name via a <title> referenced by aria-labelledby, so screen
  // readers announce it. Omit for the default decorative behaviour
  // (aria-hidden="true").
  ariaLabel?: string;
}

// A DOM id is required to point aria-labelledby at the <title>. React's
// useId gives a stable, collision-free id that survives hydration, so two
// labelled icons on one page never share a title id.

interface IconBaseProps extends IconProps {
  viewBox: string;
  fill?: string;
}

/**
 * Shared SVG shell for all icons. Maps token props to Tailwind classes so no
 * icon exposes a raw `className`, and every icon shares one interface.
 */
const IconBase: React.FC<React.PropsWithChildren<IconBaseProps>> = ({
  viewBox,
  fill = 'none',
  children,
  size = IconSize.Md,
  tone = IconTone.Inherit,
  rotate = IconRotate.None,
  transition = false,
  muted = false,
  testId,
  ariaLabel,
}) => {
  const titleId = React.useId();
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox={viewBox}
      fill={fill}
      data-testid={testId}
      aria-hidden={ariaLabel ? undefined : true}
      aria-labelledby={ariaLabel ? titleId : undefined}
      className={clsx(
        ICON_SIZE_CLASS[size],
        ICON_TONE_CLASS[tone],
        ICON_ROTATE_CLASS[rotate],
        transition && 'transition-transform',
        muted && 'opacity-50',
      )}
    >
      {ariaLabel && <title id={titleId}>{ariaLabel}</title>}
      {children}
    </svg>
  );
};

export default IconBase;
