import React, { PropsWithChildren } from 'react';

import { Card, Spacing } from 'frontend/components';

/**
 * Card surface that holds an authentication form inside the auth screen.
 */
const AuthenticationFormLayout: React.FC<PropsWithChildren> = ({
  children,
}) => (
  <Card variant="outlined" padding={Spacing.Lg}>
    {children}
  </Card>
);

export default AuthenticationFormLayout;
