import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

type HeadingLevel = 1 | 2 | 3 | 4;

interface HeadingProps {
  level?: HeadingLevel;
  truncate?: boolean;
  // Lets callers wire the heading up as an aria-labelledby target.
  id?: string;
  testId?: string;
}

const LEVEL_CLASS: Record<HeadingLevel, string> = {
  1: 'text-2xl font-bold text-content',
  2: 'text-lg font-semibold text-content',
  3: 'text-sm font-semibold text-content',
  4: 'text-xs font-semibold uppercase tracking-wide text-content-subtle',
};

const LEVEL_TAG: Record<HeadingLevel, 'h1' | 'h2' | 'h3' | 'h4'> = {
  1: 'h1',
  2: 'h2',
  3: 'h3',
  4: 'h4',
};

/**
 * Section and page headings. `level` controls both the rendered tag and the
 * type scale, so headings stay consistent and pages never pick raw text sizes.
 */
const Heading: React.FC<PropsWithChildren<HeadingProps>> = ({
  children,
  id,
  level = 2,
  testId,
  truncate = false,
}) => {
  const Tag = LEVEL_TAG[level];
  return (
    <Tag
      id={id}
      data-testid={testId}
      className={clsx(LEVEL_CLASS[level], truncate && 'truncate')}
    >
      {children}
    </Tag>
  );
};

export default Heading;
