import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

interface H2Props {
  className?: string;
}

const H2: React.FC<PropsWithChildren<H2Props>> = ({ children, className }) => (
  <h2 className={clsx("self-start pl-7 text-title-xl2 font-bold text-black", className)}>
    {children}
  </h2>
);

export default H2;
