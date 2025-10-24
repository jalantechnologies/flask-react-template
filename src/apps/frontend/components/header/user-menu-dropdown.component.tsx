import React from 'react';

import { UserMenuDropdownItem } from 'frontend/types';

type UserMenuDropdownProps = {
  dropdownOpen: boolean;
  dropdownRef: React.RefObject<HTMLDivElement>;
  setDropdownOpen: (dropdownOpen: boolean) => void;
  userMenuDropdownItems: UserMenuDropdownItem[];
};

const UserMenuDropdown: React.FC<UserMenuDropdownProps> = ({
  dropdownOpen,
  dropdownRef,
  setDropdownOpen,
  userMenuDropdownItems,
}) => (
  <div
    ref={dropdownRef}
    onFocus={() => setDropdownOpen(true)}
    onBlur={() => setDropdownOpen(false)}
    className={`absolute right-0 mt-4 flex w-55 flex-col gap-5 rounded-sm border border-stroke bg-white px-6 py-5 shadow-default dark:border-strokedark dark:bg-boxdark ${
      dropdownOpen === true ? 'block' : 'hidden'
    }`}
  >
    {userMenuDropdownItems.map((item, index) => (
      <button
        key={index}
        className="flex items-center gap-3.5  text-sm font-medium duration-300 ease-in-out hover:text-primary lg:text-base"
        onClick={item.onClick}
      >
        <img
          className="fill-current opacity-50 sm:block"
          src={item.iconPath}
          alt="logout icon"
        />
        {item.label}
      </button>
    ))}
  </div>
);

export default UserMenuDropdown;
