import React from 'react';

import {
  LayoutConfig,
  LayoutType,
} from 'frontend/components/layouts/layout-config';

interface CustomLayoutProps {
  layoutType?: LayoutType;
  children: React.ReactNode;
}

export const CustomLayout: React.FC<CustomLayoutProps> = ({
  layoutType = LayoutType.Default,
  children,
}) => {
  const LayoutComponent = LayoutConfig[layoutType] || LayoutConfig.default;

  return <LayoutComponent>{children}</LayoutComponent>;
};
