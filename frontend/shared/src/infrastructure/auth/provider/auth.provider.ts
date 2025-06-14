import { jwtDecode } from 'jwt-decode';
import { JwtDecoded } from '../../../domain/auth/value-objects/auth.vo';
import { LoginParams } from '../../../application/auth/dtos/auth.dtos';
import { apiClient } from '../../http/api-client.client';
import type {
  UserTypeBasedAuthProviderConfig,
  EnhancedAuthProvider,
} from '../config/auth-provider.config';
import { ApiErrorHandler } from '../../errorHandler/api-error.handler';
import { maskEmail } from '../../../utils/mask-email.util';

const errorHandler = new ApiErrorHandler();

const createAuthProvider = (): EnhancedAuthProvider => {
  let currentConfig: UserTypeBasedAuthProviderConfig | undefined;

  const ensureConfig = (): UserTypeBasedAuthProviderConfig => {
    if (!currentConfig) {
      throw new Error(
        'AuthProvider is not configured. Call authProvider.configure(...) first.'
      );
    }
    return currentConfig;
  };

  const handleAuthError = (error: unknown): Promise<never> => {
    try {
      errorHandler.handle(error);

      if (error instanceof Error) {
        return Promise.reject(error); // preserve original error message
      }

      return Promise.reject(new Error('Authentication failed'));
    } catch (handledError) {
      return Promise.reject(handledError);
    }
  };

  return {
    // Partial will set in shared utils based on user type
    configure(newConfig: Partial<UserTypeBasedAuthProviderConfig>) {
      const { loginPath, registerPath, expectedUserType } = newConfig;

      if (!loginPath || !registerPath || !expectedUserType) {
        throw new Error('UserTypeBasedAuthProviderConfig is incomplete.');
      }

      currentConfig = {
        loginPath,
        registerPath,
        expectedUserType,
      };
    },

    login: async ({
      username,
      password,
      user_type: expectedUserType,
    }: LoginParams) => {
      try {
        const response = await apiClient.login({ email: username, password });

        const decoded = jwtDecode<JwtDecoded>(response.data.access);
        if (expectedUserType && decoded.user_type !== expectedUserType) {
          throw new Error(
            `Only ${expectedUserType} account types can log in.`
          );
        }

        localStorage.setItem('accessToken', response.data.access);
        localStorage.setItem('refreshToken', response.data.refresh);
        localStorage.setItem('userEmail', decoded.email);
        return Promise.resolve();
      } catch (error) {
        return handleAuthError(error);
      }
    },

    checkAuth: (_params?: unknown) => {
      const config = ensureConfig();
      const currentPath = window.location.pathname;

      // Allow public paths
      if ([config.loginPath, config.registerPath].includes(currentPath)) {
        return Promise.resolve();
      }

      const token = localStorage.getItem('accessToken');
      if (!token) {
        if (currentPath !== config.loginPath) {
          window.location.replace(config.loginPath);
          return new Promise(() => { }); // Hang the promise
        }
        return Promise.reject();
      }

      try {
        const decoded = jwtDecode<JwtDecoded>(token);

        if (
          config.expectedUserType &&
          decoded.user_type !== config.expectedUserType
        ) {
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          throw new Error(
            `Access restricted to ${config.expectedUserType} users`
          );
        }

        return Promise.resolve();
      } catch (error) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        return handleAuthError(error);
      }
    },

    logout: (_params?: unknown) => {
      try {
        apiClient.logout();
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userEmail');
        return Promise.resolve();
      } catch (error) {
        return handleAuthError(error);
      }
    },

    checkError: (error) => {
      if (
        error &&
        typeof error === 'object' &&
        'status' in error &&
        [
          401, // ensures that invalid tokens don't linger in the local storage
          // 403 , It's about role, ownership, and verification, so it's not considered for now
        ].includes((error as { status: number }).status)
      ) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        return handleAuthError(error);
      }
      return Promise.resolve();
    },

    getIdentity: (_params?: unknown) => {
      try {
        const email = localStorage.getItem('userEmail');
        const maskedEmail = email ? maskEmail(email) : '';
        return Promise.resolve({
          id: email || '',
          fullName: maskedEmail || '',
          avatar: undefined,
        });
      } catch (error) {
        return handleAuthError(error);
      }
    },

    getPermissions: () => Promise.resolve(),
  };
};

export const authProvider = createAuthProvider();
