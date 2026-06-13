import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

import {
  GAP_CLASS,
  PADDING_CLASS,
} from 'frontend/components/layout/spacing-classes';
import { Spacing } from 'frontend/types/design-system';

type Align = 'start' | 'center' | 'end' | 'baseline' | 'stretch';
type Justify = 'start' | 'center' | 'end' | 'between';

interface InlineProps {
  gap?: Spacing;
  padding?: Spacing;
  align?: Align;
  justify?: Justify;
  wrap?: boolean;
  flex?: boolean;
  testId?: string;
}

const ALIGN_CLASS: Record<Align, string> = {
  start: 'items-start',
  center: 'items-center',
  end: 'items-end',
  baseline: 'items-baseline',
  stretch: 'items-stretch',
};

const JUSTIFY_CLASS: Record<Justify, string> = {
  start: 'justify-start',
  center: 'justify-center',
  end: 'justify-end',
  between: 'justify-between',
};

/**
 * Horizontal layout. Lays children left to right with a standard gap token.
 * Use this instead of writing `flex items-center gap-*` by hand.
 */
const Inline: React.FC<PropsWithChildren<InlineProps>> = ({
  align = 'center',
  children,
  flex = false,
  gap = Spacing.None,
  justify = 'start',
  padding = Spacing.None,
  wrap = false,
  testId,
}) => (
  <div
    data-testid={testId}
    className={clsx(
      'flex',
      GAP_CLASS[gap],
      PADDING_CLASS[padding],
      ALIGN_CLASS[align],
      JUSTIFY_CLASS[justify],
      wrap && 'flex-wrap',
      flex && 'flex-1',
    )}
  >
    {children}
  </div>
);

export default Inline;
