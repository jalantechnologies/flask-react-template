// Shared control surface so every text-like input (TextField, Textarea,
// Select) looks identical. Lives in its own module so no single control's
// public surface leaks the styling string to the others or to callers.
const CONTROL_CLASS =
  'w-full rounded-md border border-line bg-surface px-3 py-2 text-sm text-content placeholder-content-faint outline-none transition-colors focus:border-line-strong disabled:cursor-not-allowed disabled:bg-surface-subtle';

export default CONTROL_CLASS;
