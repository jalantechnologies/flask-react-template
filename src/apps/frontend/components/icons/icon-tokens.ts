/*
 * Icon-local design tokens. Icons are sized and toned by token props, never by
 * a raw `className`, so call-sites stay token-driven like the rest of the design
 * system. These sizes are specific to inline glyphs (size-3..size-6), so they
 * live here rather than in the shared control `Size` scale.
 */

// Glyph footprint. Covers the sizes used across all icon call-sites.
export enum IconSize {
  Xs = 'xs', // size-3
  Sm = 'sm', // size-3.5
  Md = 'md', // size-4
  Lg = 'lg', // size-5
  Xl = 'xl', // size-6
}

// Glyph colour. Defaults to inheriting the surrounding text colour; `Faint`
// dims it to the faint content tone.
export enum IconTone {
  Inherit = 'inherit',
  Faint = 'faint',
}

// Static rotation, for directional glyphs reused at a different orientation
// (e.g. a right chevron pointing down).
export enum IconRotate {
  None = 'none',
  Quarter = 'quarter', // 90deg
}

export const ICON_SIZE_CLASS: Record<IconSize, string> = {
  [IconSize.Xs]: 'size-3',
  [IconSize.Sm]: 'size-3.5',
  [IconSize.Md]: 'size-4',
  [IconSize.Lg]: 'size-5',
  [IconSize.Xl]: 'size-6',
};

export const ICON_TONE_CLASS: Record<IconTone, string> = {
  [IconTone.Inherit]: '',
  [IconTone.Faint]: 'text-content-faint',
};

export const ICON_ROTATE_CLASS: Record<IconRotate, string> = {
  [IconRotate.None]: '',
  [IconRotate.Quarter]: 'rotate-90',
};
