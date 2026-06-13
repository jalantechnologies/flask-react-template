import React from 'react';

import Center from 'frontend/components/layout/center';
import Inline from 'frontend/components/layout/inline';
import Spinner from 'frontend/components/spinner/spinner';
import Text, { Emphasis } from 'frontend/components/typography/text';
import { Spacing } from 'frontend/types/design-system';

interface LoadingProps {
  label?: string;
  fill?: boolean;
  testId?: string;
}

/** The standard centered loading indicator for page and section data fetches. */
const Loading: React.FC<LoadingProps> = ({
  fill = true,
  label = 'Loading…',
  testId,
}) => (
  <Center fill={fill}>
    <output data-testid={testId}>
      <Inline gap={Spacing.Sm} align="center">
        <Spinner decorative />
        <Text size="sm" emphasis={Emphasis.Muted}>
          {label}
        </Text>
      </Inline>
    </output>
  </Center>
);

export default Loading;
