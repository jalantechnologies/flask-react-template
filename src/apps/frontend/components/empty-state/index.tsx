import React from 'react';

import Center from 'frontend/components/layout/center';
import Inline from 'frontend/components/layout/inline';
import Stack from 'frontend/components/layout/stack';
import Heading from 'frontend/components/typography/heading';
import Text, { Emphasis } from 'frontend/components/typography/text';
import { Spacing } from 'frontend/types/design-system';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  testId?: string;
}

/**
 * The standard "nothing here yet" panel for empty lists and tables.
 * Replaces the per-page centered "No items found" divs.
 */
const EmptyState: React.FC<EmptyStateProps> = ({
  action,
  description,
  icon,
  testId,
  title,
}) => (
  <Center fill testId={testId}>
    <Stack gap={Spacing.Sm} align="center">
      {icon && <div className="text-content-faint">{icon}</div>}
      <Heading level={3}>{title}</Heading>
      {description && (
        <Text size="sm" emphasis={Emphasis.Muted}>
          {description}
        </Text>
      )}
      {action && (
        <Inline justify="center" align="center">
          {action}
        </Inline>
      )}
    </Stack>
  </Center>
);

export default EmptyState;
