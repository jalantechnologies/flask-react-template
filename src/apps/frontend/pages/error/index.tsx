import React from 'react';

import { Button, H2, ParagraphMedium } from 'frontend/components';
import { ButtonKind } from 'frontend/types/button';

type ErrorFallbackProps = {
  error: Error;
  resetError: () => void;
};

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({ resetError }) => (
  <>
    <div className="relative z-1 flex min-h-screen flex-col items-center justify-center overflow-hidden p-6">
      <div className="mx-auto w-full max-w-[242px] text-center sm:max-w-[472px]">
        <H2>ERROR</H2>

        <img
          src="/assets/img/icon/500-error-icon.svg"
          alt="500"
          className="dark:hidden"
        />

        <ParagraphMedium>
          We're sorry, but an unexpected error has occurred.
        </ParagraphMedium>

        <Button kind={ButtonKind.PRIMARY} onClick={() => resetError()}>
          Retry
        </Button>
      </div>
    </div>
  </>
);
