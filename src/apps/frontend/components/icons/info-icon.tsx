import * as React from 'react';

import IconBase, { IconProps } from 'frontend/components/icons/icon-base';

const InfoIcon: React.FC<IconProps> = (props) => (
  <IconBase viewBox="0 0 16 16" {...props}>
    <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.25" />
    <path
      d="M8 7v4M8 5.5v.5"
      stroke="currentColor"
      strokeLinecap="round"
      strokeWidth="1.25"
    />
  </IconBase>
);

export default InfoIcon;
