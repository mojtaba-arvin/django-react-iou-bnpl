export interface ApiError {
  code: number;
  message: string;
  field: string | null;
  details?: string;
}

export interface Pagination {
  total_items: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  next: string | null;
  previous: string | null;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T;
  errors: ApiError[];
  pagination?: Pagination;
}

export interface SingleResponse<T> extends ApiResponse<T> { }
export interface ListResponse<T> extends ApiResponse<T[]> {
  pagination?: Pagination;
}
