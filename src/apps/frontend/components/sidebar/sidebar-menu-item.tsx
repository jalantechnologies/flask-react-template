import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';

type SidebarMenuItemProps = {
  iconPath: string;
  path: string;
  setIsSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
  title: string;
};

const SidebarMenuItem: React.FC<SidebarMenuItemProps> = ({
  iconPath,
  path,
  title,
  setIsSidebarOpen,
}) => {
  const location = useLocation();
  const { pathname } = location;

  return (
    <li>
      <NavLink
        to={path}
        className={`group relative flex items-center gap-2.5 rounded-sm px-4 py-2 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-graydark dark:hover:bg-meta-4 ${
          pathname === path && 'bg-graydark dark:bg-meta-4'
        }`}
        onClick={() => setIsSidebarOpen(false)}
      >
        <img src={iconPath} />
        {title}
      </NavLink>
    </li>
  );
};

export default SidebarMenuItem;
