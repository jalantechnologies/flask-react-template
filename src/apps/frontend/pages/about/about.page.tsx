import React from 'react';

import { Center, Page, PageBody } from 'frontend/components';

export default function About(): React.ReactElement {
  return (
    <Page testId="about">
      <PageBody>
        <Center>
          <img id="companyLogo" src="/assets/img/logo.jpg" alt="Company logo" />
        </Center>
      </PageBody>
    </Page>
  );
}
