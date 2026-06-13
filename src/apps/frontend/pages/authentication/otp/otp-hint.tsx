import React from 'react';

import { Alert, Inline, Spacing, Status, Text } from 'frontend/components';
import InfoIcon from 'frontend/components/icons/info-icon';

interface OtpHintProps {
  otpCode?: string;
}

/**
 * A development-only notice that surfaces the default OTP code so it can be
 * entered without a real SMS. Rendered only when default OTP is enabled.
 */
const OtpHint: React.FC<OtpHintProps> = ({ otpCode }) => (
  <Alert variant={Status.Warning}>
    <Inline gap={Spacing.Sm} align="center">
      <InfoIcon ariaLabel="Information" />
      <Text as="span" size="xs">
        <strong>{otpCode}</strong> is your verification code
      </Text>
    </Inline>
  </Alert>
);

export default OtpHint;
