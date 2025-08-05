import React, { PropsWithChildren } from 'react';

const ParagraphMedium: React.FC<PropsWithChildren> = ({ children }) => (
  <p className="font-medium text-bodydark2">{children}</p>
);

export default ParagraphMedium;
