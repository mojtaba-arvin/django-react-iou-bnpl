import type {
  ComponentType,
} from 'react';
import type {
  AuthProvider,
  CatchAllComponent,
  DashboardComponent,
  DataProvider,
  LoginComponent,
  RaRecord,
  ResourceProps,
} from 'react-admin';
import type { Theme } from '@mui/material/styles';

export interface RemoteAppSetup {
  onBack?: () => void;
  basename?: AdminAppProps['basename'];
}

// utils
export interface AdminAppOptions {
  // from shell app
  onBack?: RemoteAppSetup['onBack'];
  basename?: RemoteAppSetup['basename'];

  // will add in remote app service logic
  userType: 'customer' | 'merchant';
  resources: ResourceConfig[];

  // will add in remote app service logic as needed
  dashboard?: DashboardComponent;
  customRoutes?: AdminCustomRoute[];
  theme?: Theme;
}

// admin app component props
export interface AdminAppProps {
  // from shell -> remote
  basename: string;

  // from remote
  dashboard?: AdminAppOptions['dashboard'];
  resources: AdminAppOptions['resources'];
  customRoutes?: AdminAppOptions['customRoutes'];
  theme?: AdminAppOptions['theme'];

  // will generate in utils
  authProvider: AuthProvider;
  dataProvider: DataProvider;
  loginPage: LoginComponent;
  catchAll?: CatchAllComponent;
}

type RecordToStringFunction = (record: RaRecord) => string;

export interface AdminCustomRoute {
  path: string;
  element: ComponentType;
}

export interface ResourceConfig {
  name: string;
  list?: ComponentType;
  create?: ComponentType;
  edit?: ComponentType;
  show?: ComponentType;
  icon?: ComponentType;
  recordRepresentation?: string | RecordToStringFunction;
  options?: Record<string, unknown>;
  props?: Omit<ResourceProps, 'name'>;
}
