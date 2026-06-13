import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

import { GAP_CLASS } from 'frontend/components/layout/spacing-classes';
import { Spacing } from 'frontend/types/design-system';

type Align = 'start' | 'center' | 'end' | 'stretch';
type Justify = 'start' | 'center' | 'end' | 'between';

interface StackProps {
  gap?: Spacing;
  align?: Align;
  justify?: Justify;
  flex?: boolean;
  testId?: string;
}

const ALIGN_CLASS: Record<Align, string> = {
  start: 'items-start',
  center: 'items-center',
  end: 'items-end',
  stretch: 'items-stretch',
};

const JUSTIFY_CLASS: Record<Justify, string> = {
  start: 'justify-start',
  center: 'justify-center',
  end: 'justify-end',
  between: 'justify-between',
};

/**
 * Vertical layout. Stacks children top to bottom with a standard gap token.
 * Use this instead of writing `flex flex-col gap-*` by hand.
 */
const Stack: React.FC<PropsWithChildren<StackProps>> = ({
  align = 'stretch',
  children,
  flex = false,
  gap = Spacing.None,
  justify = 'start',
  testId,
}) => (
  <div
    data-testid={testId}
    className={clsx(
      'flex flex-col',
      GAP_CLASS[gap],
      ALIGN_CLASS[align],
      JUSTIFY_CLASS[justify],
      flex && 'flex-1',
    )}
  >
    {children}
  </div>
);

export default Stack;
