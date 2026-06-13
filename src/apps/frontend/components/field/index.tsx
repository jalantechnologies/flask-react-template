import React, { PropsWithChildren } from 'react';

import { errorId, hintId } from 'frontend/components/form-control/described-by';
import Stack from 'frontend/components/layout/stack';
import Text, { Emphasis } from 'frontend/components/typography/text';
import { Spacing, Status } from 'frontend/types/design-system';

interface FieldProps {
  label?: string;
  hint?: string;
  error?: string;
  htmlFor?: string;
  testId?: string;
}

/**
 * Wraps a form control with a label, optional hint, and error message,
 * using the standard spacing token. Every input type composes this so
 * labels and validation copy look identical everywhere.
 */
const Field: React.FC<PropsWithChildren<FieldProps>> = ({
  children,
  error,
  hint,
  htmlFor,
  label,
  testId,
}) => (
  <Stack gap={Spacing.Xs} testId={testId}>
    {label && (
      <label htmlFor={htmlFor} className="block">
        <Text as="span" size="xs" weight="medium" emphasis={Emphasis.Subtle}>
          {label}
        </Text>
      </label>
    )}
    {children}
    {hint && !error && (
      <Text
        id={htmlFor ? hintId(htmlFor) : undefined}
        size="xs"
        emphasis={Emphasis.Muted}
      >
        {hint}
      </Text>
    )}
    {error && (
      <Text
        id={htmlFor ? errorId(htmlFor) : undefined}
        size="xs"
        weight="medium"
        variant={Status.Danger}
      >
        {error}
      </Text>
    )}
  </Stack>
);

export default Field;
