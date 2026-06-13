import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

import { Emphasis, Status } from 'frontend/types/design-system';

type TextSize = 'xs' | 'sm' | 'md';
type TextWeight = 'normal' | 'medium' | 'semibold';
type TextTransform = 'none' | 'capitalize' | 'uppercase';

interface TextProps {
  size?: TextSize;
  // Emphasis sets a neutral foreground by importance. For status colors
  // (success, danger, …) use `variant`, which overrides emphasis.
  emphasis?: Emphasis;
  variant?: Status;
  weight?: TextWeight;
  transform?: TextTransform;
  mono?: boolean;
  truncate?: boolean;
  // Preserve newlines and runs of whitespace (for rendered message bodies).
  preserveWhitespace?: boolean;
  breakAll?: boolean;
  // Native title tooltip; useful on truncated values.
  title?: string;
  // Lets callers wire the text up as an aria-describedby target (e.g. a field
  // hint or error referenced by its control).
  id?: string;
  testId?: string;
  as?: 'p' | 'span' | 'div';
}

const SIZE_CLASS: Record<TextSize, string> = {
  xs: 'text-xs',
  sm: 'text-sm',
  md: 'text-base',
};

const EMPHASIS_CLASS: Record<Emphasis, string> = {
  [Emphasis.Default]: 'text-content',
  [Emphasis.Subtle]: 'text-content-subtle',
  [Emphasis.Muted]: 'text-content-muted',
  [Emphasis.Inverted]: 'text-content-inverted',
};

const VARIANT_CLASS: Record<Status, string> = {
  [Status.Neutral]: 'text-content-subtle',
  [Status.Primary]: 'text-primary',
  [Status.Success]: 'text-success',
  [Status.Danger]: 'text-danger',
  [Status.Warning]: 'text-warning',
  [Status.Info]: 'text-info',
  [Status.Accent]: 'text-accent',
};

const WEIGHT_CLASS: Record<TextWeight, string> = {
  normal: 'font-normal',
  medium: 'font-medium',
  semibold: 'font-semibold',
};

const TRANSFORM_CLASS: Record<TextTransform, string> = {
  none: '',
  capitalize: 'capitalize',
  uppercase: 'uppercase',
};

/**
 * Body text. Picks size, color, and weight from tokens so copy stays
 * consistent and pages never reach for `text-xs text-gray-400`.
 */
const Text: React.FC<PropsWithChildren<TextProps>> = ({
  as = 'p',
  breakAll = false,
  children,
  emphasis = Emphasis.Default,
  id,
  mono = false,
  preserveWhitespace = false,
  size = 'sm',
  testId,
  title,
  transform = 'none',
  truncate = false,
  variant,
  weight = 'normal',
}) => {
  const Tag = as;
  return (
    <Tag
      id={id}
      title={title}
      data-testid={testId}
      className={clsx(
        SIZE_CLASS[size],
        variant ? VARIANT_CLASS[variant] : EMPHASIS_CLASS[emphasis],
        WEIGHT_CLASS[weight],
        TRANSFORM_CLASS[transform],
        mono && 'font-mono',
        truncate && 'truncate',
        breakAll && 'break-all',
        preserveWhitespace && 'whitespace-pre-wrap',
      )}
    >
      {children}
    </Tag>
  );
};

export { Emphasis, Status } from 'frontend/types/design-system';
export default Text;
