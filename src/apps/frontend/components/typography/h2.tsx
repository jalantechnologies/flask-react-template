import React, { PropsWithChildren } from 'react';

const H2: React.FC<PropsWithChildren> = ({ children }) => (
  <h2 className="self-start pl-7 text-title-xl2 font-bold text-black">
    {children}
  </h2>
);

export default H2;
