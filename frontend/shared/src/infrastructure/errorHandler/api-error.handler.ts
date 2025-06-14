import { HttpError } from 'react-admin';
import type { AxiosErrorResponse, RaError } from './error-handler.types';

export class ApiErrorHandler {
  /*
  api response body format:
      {
      "success": false,
      "message": "General error message",
      "data": {},
      "errors": [
          {
              "code": 400,
              "message": "Field 1 error",
              "field": "field1"
          },
          {
              "code": 400,
              "message": "Field 2 error",
              "field": "field2"
          }
          ]
      }

  to react-admin body format:
      {
          message: 'General error message',
          errors: {
              field1: 'Field 1 error',
              field2: 'Field 2 error'
          }
      }
  */
  handle(error: unknown): never {
    const axiosError = error as AxiosErrorResponse;
    const responseData = axiosError?.response?.data;

    if (responseData?.errors?.length) {
      const errorBody = {
        message:
          responseData.errors[0]?.message ||
          responseData.message ||
          'Validation Error',
        errors: responseData.errors.reduce(
          (acc: Record<string, string>, err: RaError) => {
            if (err.field) acc[err.field] = err.message;
            return acc;
          },
          {}
        ),
      };
      throw new HttpError(
        errorBody.message,
        axiosError.response?.status || 500,
        errorBody
      );
    }

    // Always provide a default message if none exists
    const message =
      responseData?.message || axiosError.message || 'Server Error';

    throw new HttpError(message, axiosError.response?.status || 500, {
      message,
    });
  }
}
