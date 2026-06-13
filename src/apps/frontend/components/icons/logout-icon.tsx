import * as React from 'react';

import IconBase, { IconProps } from 'frontend/components/icons/icon-base';

const LogoutIcon: React.FC<IconProps> = (props) => (
  <IconBase viewBox="0 0 16 16" {...props}>
    <path
      d="M6 2H3.5A1.5 1.5 0 002 3.5v9A1.5 1.5 0 003.5 14H6"
      stroke="currentColor"
      strokeLinecap="round"
      strokeWidth="1.25"
    />
    <path
      d="M10 11l3-3-3-3M13 8H6"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.25"
    />
  </IconBase>
);

export default LogoutIcon;
