import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens (placeholder for Epic 2)
apiClient.interceptors.request.use(
  (config) => {
    // TODO (Epic 2): Add Authorization header with JWT token
    // const token = await SecureStore.getItemAsync('auth_token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }

    if (__DEV__) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('Request timeout. Please try again.'));
    }

    if (error.code === 'ERR_NETWORK') {
      return Promise.reject(new Error('Cannot reach server. Check your connection.'));
    }

    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const message = (error.response.data as any)?.message || error.message;

      return Promise.reject(new Error(`Server error (${status}): ${message}`));
    }

    return Promise.reject(error);
  }
);

// Type definitions for common API responses
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  database: 'connected' | 'disconnected';
  redis: 'connected' | 'disconnected';
}

export interface APIError {
  message: string;
  code?: string;
  details?: any;
}

export default apiClient;
