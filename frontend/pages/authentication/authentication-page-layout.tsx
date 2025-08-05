import React, { PropsWithChildren } from 'react';

const AuthenticationPageLayout: React.FC<PropsWithChildren> = ({
  children,
}) => (
  <div className="rounded-sm border border-stroke shadow-default dark:border-strokedark dark:bg-boxdark">
    {children}
  </div>
);

export default AuthenticationPageLayout;
