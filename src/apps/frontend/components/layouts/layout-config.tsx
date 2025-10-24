import React from 'react';

export enum LayoutType {
  HalfImage = 'half-image',
  FullForm = 'full-form',
  BackgroundImage = 'background-image',
  Default = 'default',
}

/**
 * Layout 1: A layout with half an image on the left and a form on the right.
 * The image is displayed at the top on mobile and on the left side on desktop.
 */
const HalfImageHalfFormLayout: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <div className="flex min-h-screen flex-col md:flex-row">
    <div
      className="h-1/3 bg-cover bg-center md:h-auto md:w-1/2"
      style={{ backgroundImage: 'url(/assets/img/auth-background.jpg)' }}
    />
    <div className="flex w-full items-center justify-center p-4 md:w-1/2">
      <div className="w-full max-w-md">{children}</div>
    </div>
  </div>
);

/**
 * Layout 2: A layout with only a full form, no image.
 */
const FullFormLayout: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <div className="flex min-h-screen items-start justify-center p-4">
    <div className="w-full max-w-[600px] p-4">{children}</div>
  </div>
);

/**
 * Layout 3: A centered form with a semi-transparent background image.
 * The background image covers the entire screen with a dark overlay.
 */
const CenteredFormWithBackgroundLayout: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => (
  <div
    className="flex min-h-screen items-start justify-center overflow-hidden"
    style={{
      backgroundImage: 'url(/assets/img/auth-background.jpg)',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    }}
  >
    <div className="absolute inset-0 bg-black/40"></div>
    <div className="relative z-10 w-full max-w-md rounded-lg bg-black/40 p-6 shadow-lg sm:max-w-lg md:max-w-xl">
      {children}
    </div>
  </div>
);

/**
 * Default layout: A basic centered form without any background image.
 */
const DefaultLayout: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <div className="flex min-h-[60vh] items-start justify-center overflow-hidden p-4">
    <div className="w-full max-w-[550px] p-4">{children}</div>
  </div>
);

export const LayoutConfig: Record<
  string,
  React.FC<{ children: React.ReactNode }>
> = {
  [LayoutType.HalfImage]: HalfImageHalfFormLayout,
  [LayoutType.FullForm]: FullFormLayout,
  [LayoutType.BackgroundImage]: CenteredFormWithBackgroundLayout,
  [LayoutType.Default]: DefaultLayout,
};
