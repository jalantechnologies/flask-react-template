import React, { PropsWithChildren } from 'react';

const H2: React.FC<PropsWithChildren> = ({ children }) => (
  <h2 className="self-start text-title-xl2 font-bold text-black">{children}</h2>
);

export default H2;
