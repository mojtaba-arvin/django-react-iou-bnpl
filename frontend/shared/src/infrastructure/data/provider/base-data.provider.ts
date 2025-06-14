import {
  GetListResult,
  GetOneResult,
  GetManyResult,
  GetManyReferenceResult,
  CreateResult,
  UpdateResult,
  DeleteResult,
  RaRecord,
  Identifier,
  DataProvider,
  GetListParams,
  GetOneParams,
  GetManyParams,
  GetManyReferenceParams,
  CreateParams,
  UpdateParams,
  DeleteParams,
  UpdateManyParams,
  DeleteManyParams,
} from 'react-admin';
import { apiClient } from '../../http/api-client.client';
import {
  convertDeleteResponse,
  convertListResponse,
  convertSingleResponse,
  normalizeData,
} from '../../adapters/react-admin/response-converters.adapter';

export const baseDataProvider: DataProvider = {
  getList: async <RecordType extends RaRecord = RaRecord>(
    resource: string,
    params: GetListParams
  ): Promise<GetListResult<RecordType>> => {
    const filter = params.filter as Record<string, unknown> | undefined;
    const page = params.pagination?.page ?? 1;
    const page_size = params.pagination?.perPage ?? 10;
    const queryParams: Record<string, unknown> = {
      page,
      page_size,
    };

    if (filter) {
      Object.assign(queryParams, filter);
    }

    const response = await apiClient.get<RecordType[]>(`/${resource}/`, {
      params: queryParams,
    });
    return convertListResponse<RecordType>(response);
  },

  getOne: async <RecordType extends RaRecord = RaRecord>(
    resource: string,
    params: GetOneParams
  ): Promise<GetOneResult<RecordType>> => {
    const response = await apiClient.get<RecordType>(
      `/${resource}/${params.id}/`
    );
    return convertSingleResponse<RecordType>(response);
  },

  getMany: async <RecordType extends RaRecord = RaRecord>(
    resource: string,
    params: GetManyParams
  ): Promise<GetManyResult<RecordType>> => {
    const response = await apiClient.get<RecordType[]>(`/${resource}/`, {
      params: { ids: params.ids.join(',') },
    });

    return {
      data: normalizeData<RecordType>(response.data),
    };
  },

  getManyReference: async <RecordType extends RaRecord = RaRecord>(
    resource: string,
    params: GetManyReferenceParams
  ): Promise<GetManyReferenceResult<RecordType>> => {
    const queryParams = {
      [params.target]: params.id,
      page: params.pagination.page,
      page_size: params.pagination.perPage,
    };

    const response = await apiClient.get<RecordType[]>(`/${resource}/`, {
      params: queryParams,
    });

    return convertListResponse<RecordType>(response);
  },

  create: async <RecordType extends RaRecord = RaRecord>(
    resource: string,
    params: CreateParams<RecordType>
  ): Promise<CreateResult<RecordType>> => {
    const response = await apiClient.post<RecordType>(
      `/${resource}/`,
      params.data
    );
    return convertSingleResponse<RecordType>(response);
  },

  update: async <RecordType extends RaRecord = RaRecord>(
    resource: string,
    params: UpdateParams<RecordType>
  ): Promise<UpdateResult<RecordType>> => {
    const response = await apiClient.put<RecordType>(
      `/${resource}/${params.id}/`,
      params.data
    );
    return convertSingleResponse<RecordType>(response);
  },

  updateMany: async <RecordType extends RaRecord = RaRecord>(
    resource: string,
    params: UpdateManyParams<RecordType>
  ): Promise<{ data: Identifier[] }> => {
    const responses = await Promise.all(
      params.ids.map((id: Identifier) =>
        apiClient.put<{ data: { id: Identifier } }>(
          `/${resource}/${id}/`,
          params.data
        )
      )
    );

    return {
      data: responses.map((response) => response.data.data.id),
    };
  },

  delete: async <RecordType extends RaRecord = RaRecord>(
    resource: string,
    params: DeleteParams<RecordType>
  ): Promise<DeleteResult<RecordType>> => {
    const response = await apiClient.delete<RecordType>(
      `/${resource}/${params.id}/`
    );
    return convertDeleteResponse<RecordType>(response);
  },

  deleteMany: async <RecordType extends RaRecord = RaRecord>(
    resource: string,
    params: DeleteManyParams<RecordType>
  ): Promise<{ data: Identifier[] }> => {
    const responses = await Promise.all(
      params.ids.map((id: Identifier) =>
        apiClient.delete<{ data: { id: Identifier } }>(`/${resource}/${id}/`)
      )
    );

    return {
      data: responses.map((response) => response.data.data.id),
    };
  },

  payInstallment: async (id: Identifier): Promise<{ data: unknown }> => {
    const response = await apiClient.post<unknown>(`/installments/${id}/pay/`, {});
    return {
      data: response.data,
    };
  },


  getDashboardMetrics: async <RecordType extends RaRecord = RaRecord>(): Promise<
    GetOneResult<RecordType>
  > => {
    const response = await apiClient.get<RecordType>('/analytics/dashboard/');
    return convertSingleResponse<RecordType>(response);
  },
};