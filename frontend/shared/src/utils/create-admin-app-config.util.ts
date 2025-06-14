// react admin
import type { AuthProvider, CatchAllComponent, DashboardComponent, DataProvider } from 'react-admin';
import type {
  AdminAppProps,
  AdminAppOptions,
  AdminCustomRoute,
} from '../infrastructure/admin/config/admin-app.config';
import { authProvider } from '../infrastructure/auth/provider/auth.provider';
import { dataProvider } from '../infrastructure/data/provider/data-provider';
import type { UserTypeBasedAuthProviderConfig } from '../infrastructure/auth/config/auth-provider.config';
// telemetry
import { wrapDataProviderWithLogging } from '../infrastructure/telemetry/data-provider-logger.util';
import { logger } from '../infrastructure/telemetry/logger.util';
// auth pages
import { createLoginPage } from '../presentation/pages/login.page';
import { createRegisterPage } from '../presentation/pages/register.page';
import type { LoginPageProps } from '../presentation/pages/login.types';
import type { RegisterPageProps } from '../presentation/pages/register.types';
//
import { AdminError } from '../presentation/components/admin-error.component';
import { lightTheme } from '../presentation/themes/light.theme';
//
import { getGlobalSettings } from '../infrastructure/context/global-settings.context';

export const createAdminAppConfig = ({
  onBack,
  basename = '',
  userType,
  resources,
  dashboard,
  customRoutes,
  theme = lightTheme,
}: AdminAppOptions): AdminAppProps => {
  logger.info(`create an admin app config for userType: ${userType}`, {
    userType,
    basename,
  });
  const settings = getGlobalSettings();

  // Public routes without basename
  const adminBasedloginPath = `${basename}${settings.loginPath}`;
  const adminBasedregisterPath = `${basename}${settings.registerPath}`;

  const LoginPage = createLoginPage({
    userType,
    registerPath: adminBasedregisterPath,
    onBack,
  } as LoginPageProps);
  const RegisterPage = createRegisterPage({
    userType,
    loginPath: adminBasedloginPath,
    onBack,
  } as RegisterPageProps);

  // Configure auth provider
  authProvider.configure({
    loginPath: adminBasedloginPath,
    registerPath: adminBasedregisterPath,
    expectedUserType: userType,
  } as UserTypeBasedAuthProviderConfig);

  const tracedDataProvider = wrapDataProviderWithLogging(
    dataProvider as DataProvider
  );

  const defaultRegisterRoute = {
    path: settings.registerPath,
    element: RegisterPage,
  };
  const hasRegisterPath = customRoutes?.some(
    (route) => route.path === settings.registerPath
  );
  customRoutes = hasRegisterPath
    ? customRoutes
    : [...(customRoutes ?? []), defaultRegisterRoute];

  return {
    basename,
    authProvider: authProvider as AuthProvider,
    dataProvider: tracedDataProvider,
    loginPage: LoginPage,
    catchAll: AdminError as CatchAllComponent,
    dashboard: dashboard as DashboardComponent,
    resources,
    theme,
    customRoutes: customRoutes as AdminCustomRoute[],
  };
};
