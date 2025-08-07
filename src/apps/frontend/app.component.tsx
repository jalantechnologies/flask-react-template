import { ErrorBoundary } from '@datadog/browser-rum-react';
import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';

import { ErrorFallback } from './pages/error';
import { Logger } from './utils/logger';

import { AccountProvider } from 'frontend/contexts';
import { AuthProvider } from 'frontend/contexts/auth.provider';
import { Config } from 'frontend/helpers';
import { AppRoutes } from 'frontend/routes';
import InspectLet from 'frontend/vendor/inspectlet';
import Comments from './components/Comments';

Logger.init();

export default function App(): React.ReactElement {
  const [isCommentsModalOpen, setCommentsModalOpen] = useState(false);

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

          <button
            onClick={() => setCommentsModalOpen(true)}
            className="floating-comment-button"
          >
            <span className="comment-icon">💬</span>
            Comments
          </button>

          {isCommentsModalOpen && (
            <div
              style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                backgroundColor: 'rgba(0,0,0,0.5)',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: 999
              }}
              onClick={() => setCommentsModalOpen(false)}
            >
              <div
                onClick={(e) => e.stopPropagation()}
                style={{
                  position: 'relative',
                  padding: '20px',
                  borderRadius: '12px',
                  maxWidth: '700px',
                  width: '90%',
                  backgroundColor: 'white',
                  boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
                  maxHeight: '80vh',
                  overflowY: 'auto'
                }}
              >
                <button
                  onClick={() => setCommentsModalOpen(false)}
                  style={{
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    background: 'none',
                    border: 'none',
                    fontSize: '1.5rem',
                    cursor: 'pointer'
                  }}
                >&times;</button>
                <Comments taskId="temp-task-1" />
              </div>
            </div>
          )}
        </AccountProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}