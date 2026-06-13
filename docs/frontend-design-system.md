# Frontend Design System

> Building a page should feel like assembling Lego. You identify the generic
> components a screen needs, lay them out with layout primitives, and select
> presentation through tokens. You do not write CSS.

This document is the contract for all frontend UI work. It is enforced in code
review and, where possible, by lint. When a habit or a generic convention
conflicts with this file, this file wins.

## The three rules

1. **No custom CSS on pages.** A page under `src/apps/frontend/pages` must not
   style raw DOM elements with `className`, and must never use inline `style`.
   It composes design-system components and layout primitives instead. This is
   lint-enforced (`no-restricted-syntax` on `className`/`style` in `pages/**`).

2. **Select presentation through tokens, not classes.** Components expose
   `variant`, `size`, and `gap` props. You pick `variant={Variant.Primary}`,
   not a string of Tailwind classes. If you find yourself wanting a one-off
   look, the component is missing a variant. Add the variant to the component;
   do not inline it on the page.

3. **Lay out with primitives, space with gap tokens.** Vertical and horizontal
   arrangement comes from `Stack` and `Inline`. Spacing between elements comes
   from the `Spacing` scale (`xs`, `sm`, `md`, `lg`, `xl`, `xxl`), never a raw
   `gap-*` / `space-y-*` class.

## Where things live

```
src/apps/frontend/
  components/            # the design system — generic, reusable, tokenized
    layout/              # Stack, Inline, Page, PageBody, Toolbar, Grid, Center, Divider, Show, Screen
    button/ icon-button/ text-field/ textarea/ select/ field/ switch/ checkbox/ link/ menu/
    card/ badge/ status-dot/ avatar/ swatch/ alert/ modal/ confirm-dialog/
    data-table/ empty-state/ loading/ typography/
    index.ts             # the barrel — import everything from 'frontend/components'
  pages/                 # screens, assembled from components only
  types/design-system.ts # the tokens: Spacing, Variant, Size, Status, Emphasis
```

The theme (colors) is defined once in `tailwind.config.js` as semantic tokens
(`primary`, `surface`, `line`, `content`, `danger`, `success`, …). Components
reference these names, never raw palette values like `gray-900`.

## Tokens

All tokens live in `frontend/types/design-system.ts` and re-export from the
component barrel.

| Token      | Values                                               | Used by                                             |
| ---------- | ---------------------------------------------------- | --------------------------------------------------- |
| `Spacing`  | `None Xs Sm Md Lg Xl Xxl`                            | gaps and padding on layouts                         |
| `Variant`  | `Primary Secondary Tertiary Danger Ghost`            | `Button`                                            |
| `Size`     | `Sm Md Lg`                                           | `Button`, `IconButton`, `Avatar`                    |
| `Status`   | `Neutral Primary Success Danger Warning Info Accent` | `Badge`, `StatusDot`, `Alert`, `IconButton`, `Text` |
| `Emphasis` | `Default Subtle Muted Inverted`                      | `Text`                                              |

Interface conventions follow the wider ecosystem (shadcn / Radix / Bootstrap / MUI):

- Status colour is selected with a `variant` prop (not `tone`), using the `Status` token. This matches shadcn's `variant` on Badge and keeps one word across the library.
- Form controls (`TextField`, `Textarea`, `Select`) pass the **native change event** to `onChange`, like the DOM and shadcn inputs: `onChange={(e) => setX(e.target.value)}`.
- `Switch` and `Checkbox` follow Radix: `checked` + `onCheckedChange(boolean)`.
- `Avatar` takes `src` / `alt` / `fallback` (shadcn's image + fallback in one component).
- The data table is `DataTable` (a typed-column data grid), not `Table`.

## Component catalogue

Import from the barrel:

```tsx
import {
  Page,
  PageBody,
  Toolbar,
  Stack,
  Inline,
  Grid,
  Heading,
  Text,
  Button,
  TextField,
  Select,
  Card,
  Badge,
  DataTable,
  Modal,
  ConfirmDialog,
  EmptyState,
  Loading,
  Spacing,
  Variant,
  Size,
  Status,
  Emphasis,
} from 'frontend/components';
```

**Layout**

- `Page` / `PageBody` — page shell and its scrollable, padded body.
- `Stack` — vertical layout. `gap`, `align`, `justify`, `flex`.
- `Inline` — horizontal layout. `gap`, `align`, `justify`, `wrap`, `flex`.
- `Grid` — responsive grid. `base`, `md`, `gap`.
- `Toolbar` — bordered control bar for filters and page actions.
- `Center` — centers content (loading / empty regions).
- `Divider` — themed one-pixel rule.

**Typography**

- `Heading` — `level` 1–4 controls tag and scale.
- `Text` — `size`, `emphasis`, `weight`, `mono`, `truncate`.

**Controls**

- `Button` — `variant`, `size`, `fullWidth`, `isLoading`, `startIcon`.
- `IconButton` — icon-only action; requires a `label`; `variant` (status), `size`.
- `TextField` / `Textarea` / `Select` — labelled inputs sharing one control
  surface; `label`, `hint`, `error`. `onChange` receives the native event.
- `Switch` / `Checkbox` — Radix contract: `checked`, `onCheckedChange`.
- `Link` — a real anchor; `external`, `variant`.
- `Field` — label + hint + error wrapper for composing custom controls.

**Surfaces and feedback**

- `Card` — bordered surface; `variant` (`outlined`/`subtle`/`plain`), `padding`.
- `Badge` — status / role pill; `variant` (status).
- `StatusDot` — live status dot; `variant` (status).
- `Avatar` — circular image with `fallback`; `src`, `alt`, `size`.
- `Alert` — inline message; `variant` (status), `band`.
- `Modal` — overlay dialog with header, body, optional footer.
- `ConfirmDialog` — yes/no confirmation built on `Modal`.
- `DataTable` — typed-column data grid for the desktop breakpoint.
- `Menu` / `MenuItem` — dropdown with a `trigger` node.
- `EmptyState` / `Loading` — standard empty and loading regions.
- `PaginationControls` — range count + prev/next footer.

## A worked example

Before — a page hand-rolling its own input, button, and spacing:

```tsx
<div className="space-y-4">
  <label className="mb-1 block text-xs font-medium text-gray-700">App ID</label>
  <input
    className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm ..."
    value={appId}
    onChange={(e) => setAppId(e.target.value)}
  />
  <button className="rounded-md bg-gray-900 px-4 py-2 text-xs text-white ...">
    Save
  </button>
</div>
```

After — the same screen assembled from the design system:

```tsx
<Stack gap={Spacing.Md}>
  <TextField
    label="App ID"
    value={appId}
    onChange={(e) => setAppId(e.target.value)}
  />
  <Button variant={Variant.Primary} isLoading={saving} onClick={save}>
    Save
  </Button>
</Stack>
```

## Component authoring conventions

A generic component is judged by its interface, not just its output. Keep the
public API idiomatic and free of consumer-specific shaping:

- **Variants over class strings.** Expose `variant` / `size` / `tone-as-variant`
  props, not a `className`. A component's public props must never accept a
  `className` escape hatch.
- **Idiomatic prop names.** Follow the ecosystem: `variant` for status colour,
  native events on form `onChange`, Radix `onCheckedChange` for toggles,
  `src` / `fallback` for avatars. If a popular library names it, name it that.
- **Children via `PropsWithChildren`.** Never declare a `children` field in a
  Props interface. Type the component as
  `React.FC<PropsWithChildren<XProps>>`. If the content is data rather than JSX
  (a markdown string, say), make it a named prop like `content`, not children.
  This is lint-enforced.
- **No consumer-shaped methods.** The component speaks its own domain, not one
  caller's screen. If a prop only makes sense to a single consumer, the shaping
  belongs on the consumer's side.
- **A `testId` on every component.** Declare an optional `testId?: string` and
  render it as `data-testid={testId}` on the root element — icons and decorative
  primitives included. Tests address the UI through stable `data-testid` hooks,
  never text or class selectors. A component without `testId` is incomplete.
- **Accessible by construction.** Accessibility is part of the public interface.
  An interactive element is a real semantic element (`button`, `a`, `input`) or
  carries the right `role` and keyboard handling; an icon-only control exposes a
  `label` that becomes its accessible name. An icon that conveys meaning exposes
  an `ariaLabel` and drops `aria-hidden`; a decorative glyph stays `aria-hidden`
  (icons default to decorative). A form control wires up `htmlFor` /
  `aria-describedby` / `aria-invalid`, and busy/expanded/selected state is
  signalled with the matching `aria-*` attribute.

When a page needs something the catalogue does not have:

1. If it is a presentation variant of an existing component, add a `variant`
   to that component. Do not inline it on the page.
2. If it is a genuinely new generic component, build it under
   `frontend/components`, drive it with tokens, expose no raw `className` on
   its public props, and export it from the barrel.
3. If it is one-off page composition (arranging existing components), do it
   with `Stack` / `Inline` / `Grid` and gap tokens.

Components — not pages — own className and Tailwind classes. Keep the class
strings inside the component, reference theme tokens, and never accept a
`className` prop on a component's public API as an escape hatch.

## What review checks

A frontend PR is rejected if a page:

- passes `className` to a raw DOM element, or uses inline `style`;
- reaches for raw Tailwind spacing/color instead of a token or primitive;
- duplicates a component that already exists in the catalogue;
- adds a one-off look that should be a component variant.

A new or changed component is rejected if it:

- omits `testId` (no `data-testid` hook on its root), or accepts a `className`
  escape hatch on its public props;
- ships an interactive element that is not keyboard-reachable or lacks an
  accessible name (an icon-only control with no `label`, a `div` acting as a
  button, a glyph that carries meaning but stays `aria-hidden`);
- leaves a form control's label, error, or state unwired (`htmlFor` /
  `aria-describedby` / `aria-invalid` / busy/expanded state).
