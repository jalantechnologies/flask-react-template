import * as React from 'react';

import IconBase, { IconProps } from 'frontend/components/icons/icon-base';

const KeyIcon: React.FC<IconProps> = (props) => (
  <IconBase viewBox="0 0 16 16" {...props}>
    <circle cx="5" cy="5" r="3" stroke="currentColor" strokeWidth="1.25" />
    <path
      d="M7 7l6 6M11 11l1.5-1.5M13 13l1.5-1.5"
      stroke="currentColor"
      strokeWidth="1.25"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </IconBase>
);

export default KeyIcon;
