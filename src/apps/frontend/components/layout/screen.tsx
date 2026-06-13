import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

type ScreenWidth = 'xs' | 'sm' | 'md' | 'lg';

interface ScreenProps {
  // A full-viewport, tinted, centered container for standalone screens
  // (auth, onboarding, error). Caps its content column at `maxWidth`.
  maxWidth?: ScreenWidth;
  align?: 'top' | 'center';
  testId?: string;
}

const MAX_WIDTH_CLASS: Record<ScreenWidth, string> = {
  xs: 'max-w-sm',
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
};

/**
 * A standalone full-viewport screen with the app's page tint, centered, with a
 * width-capped content column. Replaces the `min-h-screen bg-gray-50 ...`
 * wrappers that auth and onboarding pages each hand-rolled.
 */
const Screen: React.FC<PropsWithChildren<ScreenProps>> = ({
  align = 'center',
  children,
  maxWidth = 'sm',
  testId,
}) => (
  <div
    data-testid={testId}
    className={clsx(
      'flex min-h-screen justify-center bg-surface-subtle px-4 py-10',
      align === 'center' ? 'items-center' : 'items-start',
    )}
  >
    <div className={clsx('w-full', MAX_WIDTH_CLASS[maxWidth])}>{children}</div>
  </div>
);

export default Screen;
