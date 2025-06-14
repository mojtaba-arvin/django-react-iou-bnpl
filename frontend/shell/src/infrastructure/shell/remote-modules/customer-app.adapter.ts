import {
  type RemoteAppSetup,
  type AdminAppProps,
  getGlobalSettings,
} from '@bnpl/shared';

export async function loadCustomerConfig(): Promise<AdminAppProps> {
  const settings = getGlobalSettings();

  const module = await import('customer_app/createAdminAppConfig');
  return module.default({
    onBack: () => (window.location.href = settings.onBackPath),
    basename: settings.customerBasePath,
  } satisfies RemoteAppSetup);
}
