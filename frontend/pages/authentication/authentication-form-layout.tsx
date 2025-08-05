import React from 'react';

import { CustomLayout } from 'frontend/components/layouts/custom-layout.component';
import { LayoutType } from 'frontend/components/layouts/layout-config';

interface AuthenticationFormLayoutProps {
  children: React.ReactNode;
  layoutType?: LayoutType;
}

const AuthenticationFormLayout: React.FC<AuthenticationFormLayoutProps> = ({
  children,
  layoutType = LayoutType.FullForm,
}) => (
  <CustomLayout layoutType={layoutType}>
    <div className="flex items-center justify-center p-4">
      <div className="w-full max-w-[550px] rounded-sm border border-stroke bg-white p-4 shadow-default dark:border-strokedark dark:bg-boxdark sm:p-4">
        {children}
      </div>
    </div>
  </CustomLayout>
);

export default AuthenticationFormLayout;
