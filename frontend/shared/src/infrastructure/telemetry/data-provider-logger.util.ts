import type { DataProvider } from 'react-admin';
import type { AttributeValue } from '@opentelemetry/api';
import { logger } from './logger.util';
import { getGlobalSettings } from '../context/global-settings.context';

type Redactable = Record<string, unknown> | null | undefined;
type DataProviderMethod = keyof DataProvider;
type DataProviderParams = Record<string, unknown> | null | undefined;
type DataProviderResult = { data?: unknown[] | Record<string, unknown> };
type LoggableData = Record<string, AttributeValue | undefined>;

const REDACTED_VALUE = '[REDACTED]';

/**
 * Redacts sensitive fields in an object by replacing values with '[REDACTED]'.
 */
const redact = (obj: Redactable): LoggableData => {
  if (!obj || typeof obj !== 'object') return {};

  const { redactedKeys } = getGlobalSettings();

  return Object.fromEntries(
    Object.entries(obj).map(([key, value]) => [
      key,
      redactedKeys.includes(key) ? REDACTED_VALUE : value as AttributeValue | undefined
    ])
  );
};

/**
 * Safely checks if a property exists in an object that might be null/undefined
 */
const hasProperty = (obj: unknown, prop: string): boolean => {
  return obj !== null && obj !== undefined && typeof obj === 'object' && prop in obj;
};

/**
 * Extracts log metadata from DataProvider parameters
 */
const extractMetadata = (params: DataProviderParams, _method: DataProviderMethod) => {
  const meta: LoggableData = {};

  if (params && typeof params === 'object') {
    if (hasProperty(params, 'id') && params.id !== undefined) {
      meta.id = typeof params.id === 'object'
        ? JSON.stringify(params.id)
        : params.id as AttributeValue;
    }

    if (hasProperty(params, 'pagination') && params.pagination) {
      meta.pagination = JSON.stringify(params.pagination);
    }

    if (hasProperty(params, 'filter') && params.filter !== undefined) {
      meta.filter = JSON.stringify(redact(params.filter as Redactable));
    }
  }

  return meta;
};

/**
 * Logs the result of a successful DataProvider call
 */
const logSuccess = (result: DataProviderResult, resource: string, method: DataProviderMethod) => {
  const count = Array.isArray(result?.data) ? result.data.length : undefined;
  logger.info(`DP success: ${method}`, { resource, op: method, count });
};

/**
 * Logs an error from a DataProvider call
 */
const logError = (error: unknown, resource: string, method: DataProviderMethod, params: DataProviderParams) => {
  const errorToLog = error instanceof Error ? error : new Error(String(error));
  logger.error(errorToLog, {
    resource,
    op: method,
    params: JSON.stringify(redact(params as Redactable))
  });
};

/**
 * Wraps a React-Admin DataProvider to add structured logging on each call.
 */
export const wrapDataProviderWithLogging = (dp: DataProvider): DataProvider => {
  return new Proxy(dp, {
    get(target, methodName: string | symbol) {
      if (typeof methodName === 'symbol') {
        return target[methodName as unknown as keyof DataProvider] as unknown;
      }

      const method = methodName as DataProviderMethod;
      const originalMethod = target[method] as ((resource: string, params?: DataProviderParams) => Promise<DataProviderResult>);

      if (typeof originalMethod !== 'function') {
        return originalMethod;
      }

      return async (resource: string, params: DataProviderParams = {}) => {
        const meta = { resource, ...extractMetadata(params, method) };
        logger.info(`DP call: ${method}`, meta);

        try {
          const result = await originalMethod(resource, params ?? {});
          logSuccess(result, resource, method);
          return result;
        } catch (error) {
          logError(error, resource, method, params);
          throw error;
        }
      };
    }
  });
};