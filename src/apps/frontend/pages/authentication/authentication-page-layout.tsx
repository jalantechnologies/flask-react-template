import React, { PropsWithChildren } from 'react';

import { Screen } from 'frontend/components';

/**
 * Full-viewport wrapper for the standalone authentication screens (login,
 * signup, OTP, password reset). Centers a width-capped column on the app tint.
 */
const AuthenticationPageLayout: React.FC<PropsWithChildren> = ({
  children,
}) => <Screen maxWidth="sm">{children}</Screen>;

export default AuthenticationPageLayout;
