import * as React from 'react';
import { useNavigate } from 'react-router-dom';

import HamburgerToggleButton from 'frontend/components/header/hamburger-toggle-button';
import UserProfileSnippet from 'frontend/components/header/user-profile-snippet.component';
import routes from 'frontend/constants/routes';
import { useAccountContext, useAuthContext } from 'frontend/contexts';
import { UserMenuDropdownItem } from 'frontend/types';

type HeaderProps = {
  isSidebarOpen: boolean;
  setIsSidebarOpen: (open: boolean) => void;
};

const Header: React.FC<HeaderProps> = ({ isSidebarOpen, setIsSidebarOpen }) => {
  const navigate = useNavigate();
  const { logout } = useAuthContext();
  const { accountDetails } = useAccountContext();

  const handleSidebarToggle = (state: boolean) => {
    setIsSidebarOpen(state);
  };

  const handleSignOut = () => {
    logout();
    navigate(routes.LOGIN);
  };

  const userMenuDropdownItems: UserMenuDropdownItem[] = [
    {
      iconPath: '/assets/img/icon/logout.svg',
      label: 'Log Out',
      onClick: handleSignOut,
    },
  ];

  return (
    <header className="sticky top-0 z-999 flex w-full bg-white drop-shadow-1 dark:bg-boxdark dark:drop-shadow-none">
      <div className="flex grow items-center justify-between p-4 shadow-2 md:px-6 2xl:px-11">
        <div className="flex items-center gap-4 lg:hidden">
          {/* Hamburger Button for sidebar */}
          <HamburgerToggleButton
            isActive={isSidebarOpen}
            onClick={handleSidebarToggle}
          />
        </div>
        <div className="flex flex-1 items-center justify-end gap-3 2xsm:gap-7">
          {/* User Area */}
          <UserProfileSnippet
            account={accountDetails}
            userMenuDropdownItems={userMenuDropdownItems}
          />
        </div>
      </div>
    </header>
  );
};
export default Header;
