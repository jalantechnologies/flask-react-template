/** @type {import('tailwindcss').Config} */

/*
 * Design tokens. Single source of truth for the UI theme.
 * Components reference semantic names (bg-primary, text-content-subtle,
 * border-line) instead of raw palette values, so the product re-themes
 * from one place and pages never need to reach for raw colors.
 *
 * See docs/frontend-design-system.md.
 */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    '!**/node_modules/**',
  ],
  theme: {
    extend: {
      colors: {
        // Primary action color: buttons, active nav, focus rings.
        primary: {
          DEFAULT: '#111827',
          hover: '#1f2937',
          muted: '#374151',
        },
        // Page and panel backgrounds.
        surface: {
          DEFAULT: '#ffffff',
          subtle: '#f9fafb',
          muted: '#f3f4f6',
        },
        // Borders and dividers.
        line: {
          DEFAULT: '#e5e7eb',
          subtle: '#f3f4f6',
          strong: '#d1d5db',
        },
        // Foreground text by emphasis.
        content: {
          DEFAULT: '#111827',
          subtle: '#6b7280',
          muted: '#9ca3af',
          faint: '#d1d5db',
          inverted: '#ffffff',
        },
        // Status tones, each with a soft background and a readable foreground.
        danger: {
          DEFAULT: '#dc2626',
          hover: '#b91c1c',
          soft: '#fef2f2',
          softText: '#dc2626',
        },
        success: {
          DEFAULT: '#16a34a',
          soft: '#f0fdf4',
          softText: '#15803d',
        },
        warning: {
          DEFAULT: '#d97706',
          soft: '#fffbeb',
          softText: '#b45309',
        },
        info: {
          DEFAULT: '#2563eb',
          soft: '#eff6ff',
          softText: '#1d4ed8',
        },
        accent: {
          DEFAULT: '#7c3aed',
          soft: '#f5f3ff',
          softText: '#6d28d9',
        },
      },
    },
  },
  plugins: [],
};
