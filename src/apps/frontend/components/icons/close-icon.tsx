import * as React from 'react';

import IconBase, { IconProps } from 'frontend/components/icons/icon-base';

const CloseIcon: React.FC<IconProps> = (props) => (
  <IconBase viewBox="0 0 24 24" {...props}>
    <path
      d="M6 6l12 12M18 6L6 18"
      stroke="currentColor"
      strokeLinecap="round"
      strokeWidth={2}
    />
  </IconBase>
);

export default CloseIcon;
