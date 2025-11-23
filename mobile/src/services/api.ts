import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens (Story 2.6)
apiClient.interceptors.request.use(
  (config) => {
    // Import here to avoid circular dependency (useAuthStore imports apiClient)
    const { useAuthStore } = require('../stores/useAuthStore');
    const token = useAuthStore.getState().token;

    // Add Authorization header if token exists
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    if (__DEV__) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and 401 auto-logout (Story 2.6)
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

      // Handle 401 Unauthorized - auto-logout
      if (status === 401) {
        // Import here to avoid circular dependency
        const { useAuthStore } = require('../stores/useAuthStore');
        const logout = useAuthStore.getState().logout;

        // Trigger logout to clear token and state (async, doesn't block error propagation)
        logout().catch((err: any) => {
          if (__DEV__) {
            console.error('Error during auto-logout:', err);
          }
          // Note: Consider error tracking service for production
          // Example: errorTrackingService.captureException(err, { context: '401_auto_logout' });
        });

        // Let error propagate for component-level handling
        return Promise.reject(new Error('Session expired. Please log in again.'));
      }

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

// Conversation types
export interface Conversation {
  id: string;
  started_at: string;
  ended_at: string | null;
  duration: number | null;
  main_topic: string | null;
}

export interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

// API functions
export const fetchConversations = async (
  page: number = 1,
  limit: number = 20
): Promise<ConversationListResponse> => {
  const response = await apiClient.get('/api/v1/conversations', {
    params: { page, limit },
  });
  return response.data;
};

export default apiClient;
