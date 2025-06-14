import {
  type RemoteAppSetup,
  type AdminAppProps,
  getGlobalSettings,
} from '@bnpl/shared';

export async function loadMerchantConfig(): Promise<AdminAppProps> {
  const settings = getGlobalSettings();

  const module = await import('merchant_app/createAdminAppConfig');
  return module.default({
    onBack: () => (window.location.href = settings.onBackPath),
    basename: settings.merchantBasePath,
  } satisfies RemoteAppSetup);
}
