import React, { useRef } from 'react';

import SidebarMenuItem from 'frontend/components/sidebar/sidebar-menu-item';
import routes from 'frontend/constants/routes';

type SidebarProps = {
  isSidebarOpen: boolean;
  setIsSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
};

const Sidebar: React.FC<SidebarProps> = ({
  isSidebarOpen,
  setIsSidebarOpen,
}) => {
  const trigger = useRef(null);
  const sidebar = useRef(null);

  return (
    <aside
      ref={sidebar}
      className={`absolute left-0 top-0 z-9999 flex h-screen w-72.5 flex-col overflow-y-hidden bg-black duration-300 ease-linear dark:bg-boxdark lg:static lg:translate-x-0 ${
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      {/* <!-- SIDEBAR HEADER --> */}
      <div className="flex items-center justify-end gap-2 px-6 py-5.5 lg:py-6.5">
        <button
          ref={trigger}
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          aria-controls="sidebar"
          aria-expanded={isSidebarOpen}
          className="block lg:hidden"
        >
          <img src="/assets/img/icon/sidebar-arrow-icon.svg" alt="arrow icon" />
        </button>
      </div>

      {/* <!-- SIDEBAR MENU --> */}
      <div className="flex flex-col overflow-y-auto duration-300 ease-linear">
        <nav className="p-2 lg:px-6">
          <h3 className="mb-2 ml-4 mt-4 text-sm font-semibold text-bodydark2">
            MENU
          </h3>
          <ul className="mb-6 flex flex-col gap-1.5">
            <SidebarMenuItem
              iconPath="/assets/img/icon/dashboard-sidebar-icon.svg"
              path={routes.DASHBOARD}
              setIsSidebarOpen={setIsSidebarOpen}
              title="Dashboard"
            />
            <SidebarMenuItem
              iconPath="/assets/img/icon/tasks-sidebar-icon.svg"
              path={routes.TASKS}
              setIsSidebarOpen={setIsSidebarOpen}
              title="Tasks"
            />
          </ul>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
