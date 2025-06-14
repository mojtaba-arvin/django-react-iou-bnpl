import { DataProvider } from 'react-admin';
import { ApiErrorHandler } from '../../../errorHandler/api-error.handler';

type DataProviderMethod = keyof DataProvider;

/**
 * Wraps a DataProvider with consistent error handling
 * @param provider - The original DataProvider to wrap
 * @param errorHandler - Error handler implementation
 * @returns A new DataProvider with error handling
 */
export const withErrorHandling = <T extends DataProvider>(
  provider: T,
  errorHandler: ApiErrorHandler
): T => {
  return new Proxy(provider, {
    get(target, prop: string | symbol) {
      const method = (target as Record<string | symbol, unknown>)[prop as DataProviderMethod] as unknown;

      // Only wrap functions
      if (typeof method !== 'function') {
        return method;
      }

      // Return wrapped async function
      return async (...args: unknown[]): Promise<unknown> => {
        try {
          return await method.apply(target, args);
        } catch (error: unknown) {
          return errorHandler.handle(error);
        }
      };
    }
  });
};