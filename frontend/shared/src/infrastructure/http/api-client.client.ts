import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
} from 'axios';
import { ApiErrorHandler } from '../errorHandler/api-error.handler';
import type { ApiResponse } from '../../domain/common/types/api-response.type';
import type { User } from '../../domain/auth/entities/auth.entities';
import type { Tokens } from '../../domain/auth/value-objects/auth.vo';
import type {
  LoginPayload,
  RegisterPayload,
} from '../../application/auth/dtos/auth.dtos';
import { getGlobalSettings } from '../context/global-settings.context';

const errorHandler = new ApiErrorHandler();

interface CustomAxiosRequestConfig extends AxiosRequestConfig {
  _retry?: boolean;
}

export class ApiClient {
  private instance: AxiosInstance;
  private refreshTokenRequest: Promise<
    AxiosResponse<ApiResponse<Tokens>>
  > | null = null;

  constructor() {
    const { apiBaseUrl } = getGlobalSettings();
    this.instance = axios.create({
      baseURL: apiBaseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.initializeInterceptors();
  }

  // Public methods
  public async get<T>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.get<ApiResponse<T>>(url, config);
    return response.data;
  }

  public async post<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.post<ApiResponse<T>>(
      url,
      data,
      config
    );
    return response.data;
  }

  public async put<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.put<ApiResponse<T>>(
      url,
      data,
      config
    );
    return response.data;
  }

  public async delete<T>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.delete<ApiResponse<T>>(url, config);
    return response.data;
  }

  // Auth methods
  public async register(data: RegisterPayload): Promise<ApiResponse<User>> {
    return this.post<User>('/auth/register/', data);
  }

  public async login(data: LoginPayload): Promise<ApiResponse<Tokens>> {
    return this.post<Tokens>('/auth/token/', data);
  }

  public async refreshToken(): Promise<ApiResponse<Tokens>> {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) throw new Error('No refresh token available');
    return this.post<Tokens>('/auth/token/refresh/', {
      refresh: refreshToken,
    });
  }

  public logout(): void {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }


  private initializeInterceptors(): void {
    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.instance.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<ApiResponse>) => {
        const originalRequest = error.config as CustomAxiosRequestConfig;

        // Handle token refresh
        /*
            {
              "success": false,
              "message": "Validation Error",
              "data": {},
              "errors": [
                {
                  "code": 401,
                  "message": "Given token not valid for any token type",
                  "field": null
                }
              ]
            }
        */
        if (
          error.response?.status === 401 &&
          error.response?.data?.errors?.some((error) =>
            error.message.includes('token')
          ) &&
          !originalRequest?.url?.includes('/auth/token/refresh') &&
          !originalRequest?._retry
        ) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refreshToken');
            if (!refreshToken) throw new Error('No refresh token available');

            if (!this.refreshTokenRequest) {
              this.refreshTokenRequest = this.instance.post(
                '/auth/token/refresh/',
                {
                  refresh: refreshToken,
                }
              );
            }

            const response = await this.refreshTokenRequest;
            this.refreshTokenRequest = null;

            if (response.data.success) {
              localStorage.setItem('accessToken', response.data.data.access);
              localStorage.setItem('refreshToken', response.data.data.refresh);

              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${response.data.data.access}`;
              }

              return this.instance(originalRequest);
            }
          } catch (refreshError) {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            return Promise.reject(refreshError);
          }
        }

        // Handle other errors
        if (error.response) {
          errorHandler.handle(error);
        }

        return Promise.reject(error);
      }
    );
  }
}

export const apiClient = new ApiClient();
