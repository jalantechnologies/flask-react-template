import clsx from 'clsx';
import React, { PropsWithChildren } from 'react';

interface ParagraphMediumProps {
  className?: string;
}

const ParagraphMedium: React.FC<PropsWithChildren<ParagraphMediumProps>> = ({ children, className }) => (
  <p className={clsx("font-medium text-bodydark2", className)}>{children}</p>
);

export default ParagraphMedium;
