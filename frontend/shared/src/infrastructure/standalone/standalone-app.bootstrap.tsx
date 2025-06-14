import React from 'react';
import ReactDOM from 'react-dom/client';
import { Route, Routes, BrowserRouter } from 'react-router-dom';
import { AdminAppProps } from '../admin/config/admin-app.config';
import { AdminApp } from '../../presentation/components/admin-app.component';
import { GlobalSettingsProvider } from '../context/global-settings.context';

export interface StandaloneAppConfigOptions {
  onBack?: () => void;
  basename?: string;
}

export interface StandaloneAppBootstrapProps {
  createAdminAppConfig: (options: StandaloneAppConfigOptions) => AdminAppProps;
  basename?: string;
}

export const StandaloneAppBootstrap: React.FC<StandaloneAppBootstrapProps> = ({
  createAdminAppConfig,
  basename = '',
}) => {
  const onBack = () => window.history.back();
  const adminAppProps = createAdminAppConfig({ onBack, basename });

  return (
    <React.StrictMode>
      <BrowserRouter basename={basename}>
        <Routes>
          <Route path="/*" element={<AdminApp {...adminAppProps} />} />
        </Routes>
      </BrowserRouter>
    </React.StrictMode>
  );
};

export const renderStandaloneApp = (
  element: HTMLElement,
  createAdminAppConfig: (options: StandaloneAppConfigOptions) => AdminAppProps,
  basename?: string
) => {
  const root = ReactDOM.createRoot(element);
  root.render(
    <React.StrictMode>
      <GlobalSettingsProvider>
        <StandaloneAppBootstrap
          createAdminAppConfig={createAdminAppConfig}
          basename={basename}
        />
      </GlobalSettingsProvider>
    </React.StrictMode>
  );
};
