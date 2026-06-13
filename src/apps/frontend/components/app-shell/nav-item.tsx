import clsx from 'clsx';
import React from 'react';
import { NavLink } from 'react-router-dom';

import Inline from 'frontend/components/layout/inline';
import Text from 'frontend/components/typography/text';
import { Spacing } from 'frontend/types/design-system';

export interface NavItemSpec {
  icon: React.ReactNode;
  label: string;
  path: string;
}

interface NavItemProps {
  item: NavItemSpec;
  onNavigate?: () => void;
  testId?: string;
}

/**
 * A single sidebar navigation row. A real router link, so it is keyboard- and
 * screen-reader-accessible and reflects the active route via aria-current.
 */
const NavItem: React.FC<NavItemProps> = ({ item, onNavigate, testId }) => (
  <NavLink
    to={item.path}
    end
    onClick={onNavigate}
    data-testid={testId}
    className={({ isActive }) =>
      clsx(
        'block rounded-md px-3 py-2 transition-colors',
        isActive
          ? 'bg-surface-muted text-content'
          : 'text-content-subtle hover:bg-surface-subtle hover:text-content',
      )
    }
  >
    <Inline gap={Spacing.Sm} align="center">
      {item.icon}
      <Text as="span" size="sm" weight="medium">
        {item.label}
      </Text>
    </Inline>
  </NavLink>
);

export default NavItem;
