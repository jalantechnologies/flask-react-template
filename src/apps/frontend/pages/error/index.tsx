import React from 'react';

import {
  Button,
  Center,
  Heading,
  Screen,
  Spacing,
  Stack,
  Text,
  Variant,
} from 'frontend/components';

type ErrorFallbackProps = {
  error: Error;
  resetError: () => void;
};

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({ resetError }) => (
  <Screen maxWidth="sm" testId="errorFallback">
    <Center>
      <Stack gap={Spacing.Md} align="center">
        <Heading level={1}>Something went wrong</Heading>
        <Text>We&apos;re sorry, but an unexpected error has occurred.</Text>
        <Button variant={Variant.Primary} onClick={() => resetError()}>
          Retry
        </Button>
      </Stack>
    </Center>
  </Screen>
);
