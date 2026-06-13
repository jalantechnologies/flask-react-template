import React from 'react';

interface SpinnerProps {
  testId?: string;
  // When the spinner sits inside a parent that already owns the live-region
  // announcement (Loading's role="status", Button's aria-busy), mark it
  // decorative so assistive tech does not announce a nested status region.
  decorative?: boolean;
}

const Spinner: React.FC<SpinnerProps> = ({ decorative = false, testId }) => (
  <div
    role={decorative ? undefined : 'status'}
    aria-label={decorative ? undefined : 'Loading'}
    aria-hidden={decorative ? true : undefined}
    data-testid={testId}
    className="
      inline-block
      size-6
      animate-spin
      rounded-full
      border-4
      border-solid
      border-current
      border-r-transparent
      align-[-0.125em]
      motion-reduce:animate-[spin_1.5s_linear_infinite]
    "
  ></div>
);

export default Spinner;
