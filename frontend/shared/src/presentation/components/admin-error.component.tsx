import type { ComponentType } from 'react';
import { logger } from '../../infrastructure/telemetry/logger.util';

// Error component for React-Admin UI errors
export const AdminError: ComponentType<{ error: Error }> = ({ error }) => {
  logger.error(error, { component: 'AdminRoot', message: error.message });
  return <div>Something went wrong: {error.message}</div>;
};
