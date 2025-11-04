import React from 'react';
import clsx from 'clsx';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white' | 'gray';
  className?: string;
  label?: string;
  centered?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className,
  label,
  centered = false,
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  const colorClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600',
    white: 'text-white',
    gray: 'text-gray-400',
  };

  const spinner = (
    <div className={clsx(
      'inline-block animate-spin rounded-full border-2 border-solid border-r-transparent',
      sizeClasses[size],
      colorClasses[color],
      className
    )}
      role="status"
      aria-label={label || 'Loading...'}
    >
      <span className="sr-only">{label || 'Loading...'}</span>
    </div>
  );

  if (centered) {
    return (
      <div className="flex items-center justify-center">
        {spinner}
      </div>
    );
  }

  return spinner;
};

// Loading overlay component
interface LoadingOverlayProps {
  isLoading: boolean;
  label?: string;
  backdrop?: boolean;
  children?: React.ReactNode;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  label = 'Loading...',
  backdrop = true,
  children,
}) => {
  if (!isLoading) {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      {children && (
        <div className={clsx('transition-opacity duration-200', backdrop && 'opacity-50')}>
          {children}
        </div>
      )}
      <div
        className={clsx(
          'absolute inset-0 flex items-center justify-center',
          backdrop && 'bg-white bg-opacity-80'
        )}
      >
        <div className="text-center">
          <LoadingSpinner size="lg" label={label} />
          {label && (
            <p className="mt-2 text-sm text-gray-600">{label}</p>
          )}
        </div>
      </div>
    </div>
  );
};

// Full page loading component
export const FullPageLoading: React.FC<{
  label?: string;
  message?: string;
}> = ({ label = 'Loading...', message }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="xl" label={label} />
        {message && (
          <p className="mt-4 text-gray-600 max-w-md">{message}</p>
        )}
      </div>
    </div>
  );
};

// Skeleton loading component
export const SkeletonLoading: React.FC<{
  lines?: number;
  className?: string;
}> = ({ lines = 3, className }) => {
  return (
    <div className={clsx('space-y-3', className)}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={clsx(
            'animate-pulse bg-gray-200 rounded',
            index === 0 ? 'h-4 w-3/4' : index === lines - 1 ? 'h-4 w-1/2' : 'h-4 w-full'
          )}
        />
      ))}
    </div>
  );
};

// Card skeleton loading
export const CardSkeletonLoading: React.FC<{
  showAvatar?: boolean;
  className?: string;
}> = ({ showAvatar = false, className }) => {
  return (
    <div className={clsx('bg-white rounded-lg shadow-sm p-6', className)}>
      <div className="animate-pulse space-y-4">
        {showAvatar && (
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        )}
        <div className="h-6 bg-gray-200 rounded w-3/4"></div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
        <div className="flex justify-between">
          <div className="h-8 bg-gray-200 rounded w-20"></div>
          <div className="h-8 bg-gray-200 rounded w-24"></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;