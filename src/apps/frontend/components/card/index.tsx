import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

import { PADDING_CLASS } from 'frontend/components/layout/spacing-classes';
import { Spacing } from 'frontend/types/design-system';

// `outlined` is a bordered white surface (the default). `subtle` adds a tinted
// background for nesting context. `plain` drops the border. Names follow the
// MUI Card `outlined` convention rather than positional inner/outer.
type CardVariant = 'outlined' | 'subtle' | 'plain';

interface CardProps {
  variant?: CardVariant;
  padding?: Spacing;
  testId?: string;
}

const VARIANT_CLASS: Record<CardVariant, string> = {
  outlined: 'rounded-md border border-line-subtle bg-surface',
  subtle: 'rounded-lg border border-line-subtle bg-surface-subtle',
  plain: 'rounded-md bg-surface',
};

/**
 * A bordered surface for grouping content. Padding comes from a spacing token
 * rather than a passed-in className, so cards are uniform across the product.
 */
const Card: React.FC<PropsWithChildren<CardProps>> = ({
  children,
  padding = Spacing.None,
  testId,
  variant = 'outlined',
}) => (
  <div
    data-testid={testId}
    className={clsx(VARIANT_CLASS[variant], PADDING_CLASS[padding])}
  >
    {children}
  </div>
);

export default Card;
