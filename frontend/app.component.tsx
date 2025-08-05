import { ErrorBoundary } from '@datadog/browser-rum-react';
import React, { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';

import { ErrorFallback } from './pages/error';
import { Logger } from './utils/logger';

import { AccountProvider } from 'frontend/contexts';
import { AuthProvider } from 'frontend/contexts/auth.provider';
import { Config } from 'frontend/helpers';
import { AppRoutes } from 'frontend/routes';
import InspectLet from 'frontend/vendor/inspectlet';

Logger.init();

export default function App(): React.ReactElement {
  useEffect(() => {
    const inspectletKey = Config.getConfigValue('inspectletKey');

    if (inspectletKey) {
      InspectLet();
    }
  }, []);

  return (
    <ErrorBoundary fallback={ErrorFallback}>
      <AuthProvider>
        <AccountProvider>
          <Toaster />
          <AppRoutes />
        </AccountProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
