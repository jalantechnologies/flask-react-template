/*
 * The design system: the complete set of generic components and layout
 * primitives. Pages build their UI from these and select presentation through
 * variant / size / status / gap tokens. Pages must not pass raw className or
 * write custom CSS. See docs/frontend-design-system.md.
 */

// Tokens
export {
  Spacing,
  Variant,
  Size,
  Status,
  Emphasis,
} from 'frontend/types/design-system';

// Layout primitives
export { default as Stack } from 'frontend/components/layout/stack';
export { default as Inline } from 'frontend/components/layout/inline';
export { default as Page } from 'frontend/components/layout/page';
export { default as PageBody } from 'frontend/components/layout/page-body';
export { default as Toolbar } from 'frontend/components/layout/toolbar';
export { default as Center } from 'frontend/components/layout/center';
export { default as Grid } from 'frontend/components/layout/grid';
export { default as Divider } from 'frontend/components/layout/divider';
export { default as Show } from 'frontend/components/layout/show';
export { default as Screen } from 'frontend/components/layout/screen';

// Typography
export { default as Heading } from 'frontend/components/typography/heading';
export { default as Text } from 'frontend/components/typography/text';

// Controls
export { default as Button } from 'frontend/components/button';
export { default as IconButton } from 'frontend/components/icon-button';
export { default as TextField } from 'frontend/components/text-field';
export { default as PasswordStrengthMeter } from 'frontend/components/password-strength-meter';
export { default as Textarea } from 'frontend/components/textarea';
export { default as Select } from 'frontend/components/select';
export { default as Field } from 'frontend/components/field';
export { default as Switch } from 'frontend/components/switch';
export { default as Checkbox } from 'frontend/components/checkbox';
export { default as Link } from 'frontend/components/link';
export { default as Otp } from 'frontend/components/otp';
export {
  default as Menu,
  MenuItem,
  MenuSection,
} from 'frontend/components/menu';

// Surfaces and feedback
export { default as Card } from 'frontend/components/card';
export { default as Badge } from 'frontend/components/badge';
export { default as StatusDot } from 'frontend/components/status-dot';
export { default as Avatar } from 'frontend/components/avatar';
export { default as Swatch } from 'frontend/components/swatch';
export { default as Alert } from 'frontend/components/alert';
export { default as Modal } from 'frontend/components/modal';
export { default as ConfirmDialog } from 'frontend/components/confirm-dialog';
export { default as DataTable } from 'frontend/components/data-table';
export { default as EmptyState } from 'frontend/components/empty-state';
export { default as Loading } from 'frontend/components/loading';
export { default as PaginationControls } from 'frontend/components/pagination-controls/pagination-controls';

// Application chrome
export { default as AppShell } from 'frontend/components/app-shell/app-shell';

export type { SelectOption } from 'frontend/components/select';
export type {
  DataTableColumn,
  DataTableProps,
} from 'frontend/components/data-table';
export type { NavItemSpec } from 'frontend/components/app-shell/nav-item';
