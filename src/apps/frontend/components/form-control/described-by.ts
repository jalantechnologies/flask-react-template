// Derives the stable ids that associate a control with its Field-rendered hint
// and error text. Field assigns these ids to the hint/error nodes; each control
// (TextField, Textarea, Select) points aria-describedby at the same ids, so the
// message a sighted user reads is announced to a screen reader too. Both sides
// derive from the control id, keeping them in sync with no shared state.

interface FieldDescription {
  // Whether a hint is shown (suppressed when an error is present).
  hint: boolean;
  error: boolean;
}

const hintId = (controlId: string): string => `${controlId}-hint`;

const errorId = (controlId: string): string => `${controlId}-error`;

/**
 * The aria-describedby value for a control, or undefined when it has no
 * description. Error takes precedence over hint, matching Field's render rule
 * (hint is hidden while an error is shown).
 */
const describedBy = (
  controlId: string,
  { error, hint }: FieldDescription,
): string | undefined => {
  if (error) {
    return errorId(controlId);
  }
  if (hint) {
    return hintId(controlId);
  }
  return undefined;
};

export { describedBy, errorId, hintId };
