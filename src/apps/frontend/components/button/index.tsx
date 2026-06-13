import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

import Spinner from 'frontend/components/spinner/spinner';
import { ButtonType } from 'frontend/types/button';
import { Size, Variant } from 'frontend/types/design-system';

interface ButtonProps {
  variant?: Variant;
  size?: Size;
  type?: ButtonType;
  disabled?: boolean;
  isLoading?: boolean;
  fullWidth?: boolean;
  startIcon?: React.ReactNode;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  title?: string;
  testId?: string;
}

const BASE =
  'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50';

const VARIANT_CLASS: Record<Variant, string> = {
  [Variant.Primary]: 'bg-primary text-content-inverted hover:bg-primary-hover',
  [Variant.Secondary]:
    'border border-line-strong bg-surface text-content hover:bg-surface-subtle',
  [Variant.Tertiary]: 'bg-transparent text-primary hover:text-primary-muted',
  [Variant.Danger]: 'bg-danger text-content-inverted hover:bg-danger-hover',
  [Variant.Ghost]:
    'bg-transparent text-content-subtle hover:bg-surface-muted hover:text-content',
};

const SIZE_CLASS: Record<Size, string> = {
  [Size.Sm]: 'px-3 py-1.5 text-xs',
  [Size.Md]: 'px-4 py-2 text-sm',
  [Size.Lg]: 'px-5 py-2.5 text-base',
};

/**
 * The single button primitive. Presentation comes from `variant` and `size`
 * tokens; pages never style a `<button>` by hand or pass raw classes.
 */
const Button: React.FC<PropsWithChildren<ButtonProps>> = ({
  children,
  disabled = false,
  fullWidth = false,
  isLoading = false,
  onClick,
  size = Size.Md,
  startIcon,
  testId,
  title,
  type = ButtonType.BUTTON,
  variant = Variant.Primary,
}) => (
  <button
    className={clsx(
      BASE,
      VARIANT_CLASS[variant],
      SIZE_CLASS[size],
      fullWidth && 'w-full',
    )}
    disabled={disabled || isLoading}
    aria-busy={isLoading || undefined}
    title={title}
    type={type}
    data-testid={testId}
    onClick={onClick}
  >
    {isLoading ? (
      <Spinner decorative />
    ) : (
      <>
        {startIcon}
        {children}
      </>
    )}
  </button>
);

export default Button;
