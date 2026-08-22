import { readFileSync } from 'node:fs';
import path from 'node:path';

import { describe, expect, it } from 'vitest';

const stylesheet = readFileSync(path.resolve(__dirname, 'style.css'), 'utf-8');

describe('style.css reduced motion', () => {
  it('declares a prefers-reduced-motion reduce block', () => {
    expect(stylesheet).toContain('@media (prefers-reduced-motion: reduce)');
  });

  it('neutralises animations, transitions and smooth scrolling inside that block', () => {
    const block = stylesheet.slice(
      stylesheet.indexOf('@media (prefers-reduced-motion: reduce)'),
    );

    expect(block).toContain('animation-duration: 0.01ms !important');
    expect(block).toContain('animation-iteration-count: 1 !important');
    expect(block).toContain('transition-duration: 0.01ms !important');
    expect(block).toContain('scroll-behavior: auto !important');
  });

  it('keeps the overrides scoped to the media query rather than applying globally', () => {
    const beforeMediaQuery = stylesheet.slice(
      0,
      stylesheet.indexOf('@media (prefers-reduced-motion: reduce)'),
    );

    expect(beforeMediaQuery).not.toContain('animation-duration');
    expect(beforeMediaQuery).not.toContain('transition-duration');
  });

  it('applies the overrides after the tailwind layers so they win', () => {
    expect(stylesheet.indexOf('@tailwind utilities')).toBeLessThan(
      stylesheet.indexOf('@media (prefers-reduced-motion: reduce)'),
    );
  });
});
