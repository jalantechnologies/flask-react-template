import * as React from 'react';

import IconBase, { IconProps } from 'frontend/components/icons/icon-base';

const MenuIcon: React.FC<IconProps> = (props) => (
  <IconBase viewBox="0 0 24 24" {...props}>
    <path
      d="M4 6h16M4 12h16M4 18h16"
      stroke="currentColor"
      strokeLinecap="round"
      strokeWidth={2}
    />
  </IconBase>
);

export default MenuIcon;
