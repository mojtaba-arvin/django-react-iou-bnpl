export interface RaError {
  field?: string;
  message: string;
}

export interface AxiosErrorData {
  message?: string;
  errors?: RaError[];
}

export interface AxiosErrorResponse {
  response?: {
    status: number;
    data: AxiosErrorData;
  };
  message?: string;
}
