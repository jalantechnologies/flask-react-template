/*
 * Shared design-system tokens. Every generic component and layout primitive
 * draws its variants, sizes, tones, and spacing from this file so the whole
 * UI speaks one vocabulary. Pages select a token; they never hand-write the
 * underlying Tailwind classes.
 */

// Spacing scale used by layout primitives (gap) and section padding.
// Maps a human-readable size to a fixed Tailwind gap, so pages say
// `gap={Spacing.Md}` instead of guessing a number.
export enum Spacing {
  None = 'none',
  Xs = 'xs',
  Sm = 'sm',
  Md = 'md',
  Lg = 'lg',
  Xl = 'xl',
  Xxl = 'xxl',
}

// Button / actionable element visual variants.
export enum Variant {
  Primary = 'primary',
  Secondary = 'secondary',
  Tertiary = 'tertiary',
  Danger = 'danger',
  Ghost = 'ghost',
}

// Control sizing, shared by Button, Input, Select, IconButton.
export enum Size {
  Sm = 'sm',
  Md = 'md',
  Lg = 'lg',
}

// Status palette, shared by Badge, Alert, StatusDot, and IconButton. Exposed
// through a `variant` prop (shadcn/Bootstrap convention) on those components.
export enum Status {
  Neutral = 'neutral',
  Primary = 'primary',
  Success = 'success',
  Danger = 'danger',
  Warning = 'warning',
  Info = 'info',
  Accent = 'accent',
}

// Text emphasis, shared by Text / Heading typography.
export enum Emphasis {
  Default = 'default',
  Subtle = 'subtle',
  Muted = 'muted',
  Inverted = 'inverted',
}
