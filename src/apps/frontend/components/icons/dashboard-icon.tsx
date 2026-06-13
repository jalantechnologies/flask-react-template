import * as React from 'react';

import IconBase, { IconProps } from 'frontend/components/icons/icon-base';

const DashboardIcon: React.FC<IconProps> = (props) => (
  <IconBase viewBox="0 0 16 16" {...props}>
    <rect
      x="2"
      y="2"
      width="5"
      height="5"
      rx="1"
      stroke="currentColor"
      strokeWidth="1.25"
    />
    <rect
      x="9"
      y="2"
      width="5"
      height="5"
      rx="1"
      stroke="currentColor"
      strokeWidth="1.25"
    />
    <rect
      x="2"
      y="9"
      width="5"
      height="5"
      rx="1"
      stroke="currentColor"
      strokeWidth="1.25"
    />
    <rect
      x="9"
      y="9"
      width="5"
      height="5"
      rx="1"
      stroke="currentColor"
      strokeWidth="1.25"
    />
  </IconBase>
);

export default DashboardIcon;
