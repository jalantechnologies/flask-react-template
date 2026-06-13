import React from 'react';

import Avatar from 'frontend/components/avatar';
import LogoutIcon from 'frontend/components/icons/logout-icon';
import Inline from 'frontend/components/layout/inline';
import Stack from 'frontend/components/layout/stack';
import Menu, { MenuItem, MenuSection } from 'frontend/components/menu';
import Text, { Emphasis } from 'frontend/components/typography/text';
import { Spacing } from 'frontend/types/design-system';

interface UserMenuProps {
  name: string;
  email: string;
  onSignOut: () => void;
  testId?: string;
}

/** The signed-in user's avatar with a dropdown for account actions. */
const UserMenu: React.FC<UserMenuProps> = ({
  email,
  name,
  onSignOut,
  testId,
}) => {
  const initials = name
    .split(' ')
    .map((part) => part.charAt(0))
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <Menu
      align="right"
      ariaLabel="Open user menu"
      trigger={<Avatar fallback={initials || 'U'} />}
      testId={testId}
    >
      <MenuSection border="bottom">
        <Stack gap={Spacing.Xs}>
          <Text size="sm" weight="medium">
            {name}
          </Text>
          <Text size="xs" emphasis={Emphasis.Muted}>
            {email}
          </Text>
        </Stack>
      </MenuSection>
      <MenuItem onClick={onSignOut} testId="signOut">
        <Inline gap={Spacing.Sm} align="center">
          <LogoutIcon />
          Log Out
        </Inline>
      </MenuItem>
    </Menu>
  );
};

export default UserMenu;
