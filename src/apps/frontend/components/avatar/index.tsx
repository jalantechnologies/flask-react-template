import clsx from 'clsx';
import React from 'react';

import { Size } from 'frontend/types/design-system';

interface AvatarProps {
  // Optional image; when absent or it fails to load, `fallback` shows instead.
  src?: string;
  alt?: string;
  // Text shown when there is no image (typically initials). Required so the
  // avatar always renders something meaningful.
  fallback: string;
  // shadcn's Avatar has no size prop; we keep one because the product needs a
  // small/medium/large scale and a token is cleaner than a passed className.
  size?: Size;
  testId?: string;
}

const SIZE_CLASS: Record<Size, string> = {
  [Size.Sm]: 'size-7 text-xs',
  [Size.Md]: 'size-8 text-xs',
  [Size.Lg]: 'size-10 text-sm',
};

/**
 * A circular avatar: renders `src` when available, otherwise the `fallback`
 * text. Composition mirrors shadcn's AvatarImage + AvatarFallback in a single
 * prop-driven component.
 */
const Avatar: React.FC<AvatarProps> = ({
  alt,
  fallback,
  size = Size.Md,
  src,
  testId,
}) => (
  <span
    data-testid={testId}
    className={clsx(
      'inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-surface-muted font-semibold text-content-subtle',
      SIZE_CLASS[size],
    )}
  >
    {src ? (
      <img src={src} alt={alt ?? fallback} className="size-full object-cover" />
    ) : (
      fallback
    )}
  </span>
);

export default Avatar;
