import React from 'react';
import ReactDOM from 'react-dom/client';
import { Suspense, useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useMediaQuery, useTheme } from '@mui/material';
import {
  AdminApp,
  ErrorBoundary,
  getGlobalSettings,
  GlobalSettingsProvider,
  initializeTracing,
  logger,
  registerAutoInstrumentations,
  useGlobalSettings,
  type AdminAppProps,
} from '@bnpl/shared';
import { HomePage } from '../../presentation/pages/home.page';
import { loadCustomerConfig } from './remote-modules/customer-app.adapter';
import { loadMerchantConfig } from './remote-modules/merchant-app.adapter';

/**
 * Shell application loads remote AdminApp configs for customer and merchant,
 * wraps them in ErrorBoundary and Suspense, and mounts under routes.
 */
function App() {
  const { customerBasePath, merchantBasePath } = useGlobalSettings();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [customerAdminProps, setCustomerAdminProps] =
    useState<AdminAppProps | null>(null);
  const [merchantAdminProps, setMerchantAdminProps] =
    useState<AdminAppProps | null>(null);

  useEffect(() => {
    loadCustomerConfig().then(setCustomerAdminProps);
    loadMerchantConfig().then(setMerchantAdminProps);
  }, []);

  if (!customerAdminProps || !merchantAdminProps) {
    return <div>Loading...</div>;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage isMobile={isMobile} />} />
        <Route
          path={`${customerBasePath}/*`}
          element={
            <ErrorBoundary>
              <Suspense fallback={<div>Loading application...</div>}>
                <AdminApp {...customerAdminProps} />
              </Suspense>
            </ErrorBoundary>
          }
        />
        <Route
          path={`${merchantBasePath}/*`}
          element={
            <ErrorBoundary>
              <Suspense fallback={<div>Loading application...</div>}>
                <AdminApp {...merchantAdminProps} />
              </Suspense>
            </ErrorBoundary>
          }
        />
        {/* <Route path="*" element={<Navigate to="/" />} /> */}
      </Routes>
    </BrowserRouter>
  );
}

// Initialize tracing and auto-instrumentations
const settings = getGlobalSettings();
initializeTracing();
registerAutoInstrumentations();
logger.info('Telemetry initialized in entry point', {
  ...settings,
});

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(
  <React.StrictMode>
    <GlobalSettingsProvider value={settings}>
      <App />
    </GlobalSettingsProvider>
  </React.StrictMode>
);
