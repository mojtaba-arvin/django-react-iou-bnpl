import {
  DeleteResult,
  GetListResult,
  GetOneResult,
  RaRecord,
} from 'react-admin';
import {
  ApiResponse,
  ListResponse,
  SingleResponse,
} from '../../../domain/common/types/api-response.type';

export const normalizeData = <T>(data: unknown): T[] => {
  if (Array.isArray(data)) return data as T[];
  if (
    typeof data === 'object' &&
    data !== null &&
    Object.keys(data).length === 0
  ) {
    return [];
  }
  throw new Error(`Expected array but got ${typeof data}`);
};

// Convert list responses (with pagination)
export const convertListResponse = <RecordType extends RaRecord = RaRecord>(
  response: ListResponse<RecordType>
): GetListResult<RecordType> => {
  if (!response.success) throw new Error(response.message);

  const data = normalizeData<RecordType>(response.data);
  return {
    data,
    total: response.pagination?.total_items || data.length,
    pageInfo: {
      hasNextPage: !!response.pagination?.next,
      hasPreviousPage: !!response.pagination?.previous,
    },
  };
};

// Convert single record responses
export const convertSingleResponse = <RecordType extends RaRecord = RaRecord>(
  response: SingleResponse<RecordType> // Use SingleResponse type
): GetOneResult<RecordType> => {
  if (!response.success) {
    const errorMessage = response.errors[0]?.message || response.message;
    throw new Error(errorMessage);
  }

  return {
    data: response.data,
  };
};

// Convert delete responses
export const convertDeleteResponse = <RecordType extends RaRecord = RaRecord>(
  response: ApiResponse<RecordType>
): DeleteResult<RecordType> => {
  if (!response.success) {
    throw new Error(response.message);
  }

  return {
    data: response.data,
  };
};
