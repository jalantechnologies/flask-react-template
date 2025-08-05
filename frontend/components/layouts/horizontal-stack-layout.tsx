import React, { PropsWithChildren } from 'react';

interface HorizontalStackLayoutProps {
  gap?: number;
}

const HorizontalStackLayout: React.FC<
  PropsWithChildren<HorizontalStackLayoutProps>
> = ({ children, gap = 0 }) => (
  <div className={`gap-${gap} flex items-center`}>{children}</div>
);

export default HorizontalStackLayout;
