import { Spacing } from 'frontend/types/design-system';

/*
 * Tailwind class strings for the Spacing scale. These live in the rendering
 * layer (not the token/types file) so importing a token enum for type checking
 * never pulls in class-string implementation details.
 */

export const GAP_CLASS: Record<Spacing, string> = {
  [Spacing.None]: 'gap-0',
  [Spacing.Xs]: 'gap-1',
  [Spacing.Sm]: 'gap-2',
  [Spacing.Md]: 'gap-4',
  [Spacing.Lg]: 'gap-6',
  [Spacing.Xl]: 'gap-8',
  [Spacing.Xxl]: 'gap-12',
};

export const PADDING_CLASS: Record<Spacing, string> = {
  [Spacing.None]: 'p-0',
  [Spacing.Xs]: 'p-1',
  [Spacing.Sm]: 'p-2',
  [Spacing.Md]: 'p-4',
  [Spacing.Lg]: 'p-6',
  [Spacing.Xl]: 'p-8',
  [Spacing.Xxl]: 'p-12',
};
