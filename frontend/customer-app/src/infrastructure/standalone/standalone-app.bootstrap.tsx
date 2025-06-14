import { renderStandaloneApp } from '@bnpl/shared';
import { default as createAdminAppConfig } from '../../application/services/create-admin-app-config.service';

renderStandaloneApp(
  document.getElementById('root')!,
  createAdminAppConfig,
  ''
);
