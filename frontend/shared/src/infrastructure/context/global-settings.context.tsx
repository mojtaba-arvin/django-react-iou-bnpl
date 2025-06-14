import { createContext, useContext, ReactNode } from 'react';

type GlobalSettings = {
  nodeEnv: 'development' | 'production';
  apiBaseUrl: string;
  currency: string;
  locale: string;
  telemetryExporterUrl: string;
  onBackPath: string;
  customerBasePath: string;
  merchantBasePath: string;
  loginPath: string;
  registerPath: string;
  // Sensitive keys to redact from log metadata
  // Derived from payload structures: RegisterPayload, LoginPayload, Tokens
  redactedKeys: Array<string>;
};

// needs to define in webpack DefinePlugin of shell and standalone remotes
export const getGlobalSettings = (): GlobalSettings => {
  return {
    nodeEnv:
      process.env.NODE_ENV === 'production' ? 'production' : 'development',
    apiBaseUrl:
      process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
    currency: process.env.REACT_APP_CURRENCY || 'USD',
    locale: process.env.REACT_APP_LOCALE || 'en-US',
    telemetryExporterUrl: process.env.REACT_APP_TELEMETRY_EXPORTER_URL || '',
    onBackPath: '/',
    customerBasePath: '/customer',
    merchantBasePath: '/merchant',
    loginPath: '/login',
    registerPath: '/register',
    redactedKeys: ['password', 'access', 'refresh'],
  };
};

const defaultSettings: GlobalSettings = getGlobalSettings();

const GlobalSettingsContext = createContext<GlobalSettings>(defaultSettings);

export const useGlobalSettings = () => useContext(GlobalSettingsContext);

export const GlobalSettingsProvider = ({
  children,
  value,
}: {
  children: ReactNode;
  value?: Partial<GlobalSettings>;
}) => {
  const mergedSettings = { ...defaultSettings, ...value };
  return (
    <GlobalSettingsContext.Provider value={mergedSettings}>
      {children}
    </GlobalSettingsContext.Provider>
  );
};
