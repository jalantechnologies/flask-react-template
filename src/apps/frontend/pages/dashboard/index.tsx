import * as React from 'react';

import {
  Heading,
  Page,
  PageBody,
  Spacing,
  Stack,
  Text,
} from 'frontend/components';

const Dashboard: React.FC = () => (
  <Page testId="dashboard">
    <PageBody>
      <Stack gap={Spacing.Sm}>
        <Heading level={1}>Dashboard</Heading>
        <Text>Welcome back. This is your dashboard.</Text>
      </Stack>
    </PageBody>
  </Page>
);

export default Dashboard;
