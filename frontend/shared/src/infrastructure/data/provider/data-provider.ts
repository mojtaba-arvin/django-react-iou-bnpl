import { ApiErrorHandler } from '../../errorHandler/api-error.handler';
import { withErrorHandling } from './decorators/with-error-handling.decorator';
import { baseDataProvider } from './base-data.provider';

const errorHandler = new ApiErrorHandler();

export const dataProvider = withErrorHandling(baseDataProvider, errorHandler);
