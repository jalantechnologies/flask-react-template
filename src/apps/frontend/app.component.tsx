import { ErrorBoundary } from '@datadog/browser-rum-react';
import React, { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { ErrorFallback } from './pages/error';
import { Logger } from './utils/logger';

import { AccountProvider } from 'frontend/contexts';
import { AuthProvider } from 'frontend/contexts/auth.provider';
import { Config } from 'frontend/helpers';
import InspectLet from 'frontend/vendor/inspectlet';

// Import your comment page
import CommentManager from 'frontend/pages/comments/CommentManager';

// Import other routes (assuming AppRoutes contains default routes)
import { AppRoutes } from 'frontend/routes';

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
          <BrowserRouter>
            <Routes>
              {/* Default App routes */}
              <Route path="/*" element={<AppRoutes />} />

              {/* New Comment Manager route */}
              <Route path="/comments" element={<CommentManager />} />
            </Routes>
          </BrowserRouter>
        </AccountProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
