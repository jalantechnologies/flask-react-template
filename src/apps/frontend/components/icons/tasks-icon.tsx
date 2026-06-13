import * as React from 'react';

import IconBase, { IconProps } from 'frontend/components/icons/icon-base';

const TasksIcon: React.FC<IconProps> = (props) => (
  <IconBase viewBox="0 0 16 16" {...props}>
    <path
      d="M6 4h8M6 8h8M6 12h8"
      stroke="currentColor"
      strokeLinecap="round"
      strokeWidth="1.25"
    />
    <path
      d="M2 4h.01M2 8h.01M2 12h.01"
      stroke="currentColor"
      strokeLinecap="round"
      strokeWidth="1.5"
    />
  </IconBase>
);

export default TasksIcon;
