import type { AuthProvider } from 'react-admin';

export interface EnhancedAuthProvider extends AuthProvider {
  configure: (config: Partial<UserTypeBasedAuthProviderConfig>) => void;
}

export interface UserTypeBasedAuthProviderConfig {
  loginPath: string;
  registerPath: string;
  expectedUserType?: string;
}
