import React from 'react';

import InfoIcon from 'frontend/components/icons/info-icon';

interface OtpHintProps {
  otpCode?: string;
}

const OtpHint: React.FC<OtpHintProps> = ({ otpCode }) => (
  <div className="mx-2 flex items-center rounded-lg text-sm text-orange-500">
    <InfoIcon className="me-3 inline size-4 shrink-0 fill-current text-orange-500" />
    <span>
      <strong>{otpCode}</strong> is your verification code
    </span>
  </div>
);

export default OtpHint;
