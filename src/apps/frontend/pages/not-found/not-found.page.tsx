import React from 'react';

import { EmptyState, Page, PageBody } from 'frontend/components';

export default function NotFound(): React.ReactElement {
  return (
    <Page testId="notFoundContainer">
      <PageBody>
        <EmptyState
          title="Page not found"
          description="The page you are looking for does not exist."
        />
      </PageBody>
    </Page>
  );
}
