import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

interface LinkProps {
  href: string;
  external?: boolean;
  // Visual treatment: `inline` underlines within body copy; `subtle` is a
  // quiet link (footer chrome); `plain` carries no underline; `primary`
  // renders the link styled like the primary button (for a URL navigation CTA,
  // so it keeps native middle-click, open-in-new-tab and copy-link).
  variant?: 'inline' | 'subtle' | 'plain' | 'primary';
  // Stretch a `primary` CTA link to the full width of its container.
  fullWidth?: boolean;
  title?: string;
  testId?: string;
  ariaLabel?: string;
}

const VARIANT_CLASS: Record<NonNullable<LinkProps['variant']>, string> = {
  inline: 'text-content underline underline-offset-2 hover:text-primary',
  subtle: 'text-content-muted hover:text-content-subtle',
  plain: 'text-content no-underline hover:opacity-70',
  primary:
    'inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium bg-primary text-content-inverted no-underline hover:bg-primary-hover',
};

/**
 * An anchor. Use this for real navigation to a URL (keeps native middle-click,
 * open-in-new-tab, copy-link) instead of a Button. External links get
 * target=_blank with safe rel. The `primary` variant styles it as a button for
 * a navigation CTA.
 */
const Link: React.FC<PropsWithChildren<LinkProps>> = ({
  ariaLabel,
  children,
  external = false,
  fullWidth = false,
  href,
  testId,
  title,
  variant = 'inline',
}) => (
  <a
    href={href}
    title={title}
    target={external ? '_blank' : undefined}
    rel={external ? 'noopener noreferrer' : undefined}
    aria-label={ariaLabel}
    data-testid={testId}
    className={clsx(
      'transition-colors',
      VARIANT_CLASS[variant],
      fullWidth && 'w-full',
    )}
  >
    {children}
  </a>
);

export default Link;
