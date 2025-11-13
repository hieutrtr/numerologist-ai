/**
 * API Service - Backend Communication
 *
 * Handles all HTTP requests to the backend API.
 * Includes authentication, error handling, and response parsing.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// TODO: Update with your backend URL
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000/api/v1'  // Development
  : 'https://your-api.com/api/v1';   // Production

/**
 * API Response Types
 */
export interface ConversationStartResponse {
  conversation_id: string;
  daily_room_url: string;
  daily_token: string;
}

export interface ConversationEndResponse {
  message: string;
  conversation_id: string;
}

export interface ApiError {
  detail: string;
  status: number;
}

/**
 * API Client Class
 */
class ApiClient {
  private client: AxiosInstance;
  private authToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - Add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - Handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const apiError: ApiError = {
          detail: error.response?.data?.detail || error.message || 'Unknown error',
          status: error.response?.status || 500,
        };
        return Promise.reject(apiError);
      }
    );
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string | null) {
    this.authToken = token;
  }

  /**
   * Start a new voice conversation
   *
   * @returns Promise with room URL and token
   * @throws ApiError if request fails
   */
  async startConversation(): Promise<ConversationStartResponse> {
    try {
      const response = await this.client.post<ConversationStartResponse>(
        '/conversations/start'
      );
      return response.data;
    } catch (error) {
      console.error('Failed to start conversation:', error);
      throw error;
    }
  }

  /**
   * End an active conversation
   *
   * @param conversationId - UUID of the conversation to end
   * @returns Promise with confirmation message
   * @throws ApiError if request fails
   */
  async endConversation(conversationId: string): Promise<ConversationEndResponse> {
    try {
      const response = await this.client.post<ConversationEndResponse>(
        `/conversations/${conversationId}/end`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to end conversation:', error);
      throw error;
    }
  }

  /**
   * Health check - Test API connectivity
   *
   * @returns Promise<boolean> - True if API is healthy
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get('/health');
      return true;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export for testing
export default ApiClient;
