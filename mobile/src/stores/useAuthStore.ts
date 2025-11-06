import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';
import { apiClient } from '../services/api';
import { User, RegisterData, AuthResponse, AuthState } from '../types/user.types';

const AUTH_TOKEN_KEY = 'auth_token';

/**
 * Zustand auth store for managing user authentication state and token persistence
 *
 * State:
 * - user: Current authenticated user or null
 * - token: JWT access token or null
 * - isAuthenticated: Boolean indicating authentication status
 * - isLoading: Boolean indicating if auth state is being checked
 *
 * Actions:
 * - login(email, password): Authenticate user and store token
 * - register(data): Create new user account and store token
 * - logout(): Clear authentication state and token
 * - checkAuth(): Validate token on app load
 */
export const useAuthStore = create<AuthState>((set, get) => ({
  // Initial state
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true, // Start as loading for checkAuth on app load

  // Login action: authenticate with email and password
  login: async (email: string, password: string) => {
    try {
      set({ isLoading: true });

      // Call login endpoint
      const response = await apiClient.post<AuthResponse>('/api/v1/auth/login', {
        email,
        password,
      });

      const { user, access_token } = response.data;

      // Store token in SecureStore (encrypted)
      await SecureStore.setItemAsync(AUTH_TOKEN_KEY, access_token);

      // Update store state
      set({
        user,
        token: access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  // Register action: create new account and authenticate
  register: async (data: RegisterData) => {
    try {
      set({ isLoading: true });

      // Call registration endpoint
      const response = await apiClient.post<AuthResponse>('/api/v1/auth/register', data);

      const { user, access_token } = response.data;

      // Store token in SecureStore (encrypted)
      await SecureStore.setItemAsync(AUTH_TOKEN_KEY, access_token);

      // Update store state
      set({
        user,
        token: access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  // Logout action: clear authentication state and delete token
  logout: async () => {
    try {
      // Delete token from SecureStore
      await SecureStore.deleteItemAsync(AUTH_TOKEN_KEY);
    } catch (error) {
      // Log error but don't throw - logout should always succeed
      if (__DEV__) {
        console.error('Error deleting token from SecureStore:', error);
      }

      // In production, consider sending to error tracking service (e.g., Sentry)
      // Example: errorTrackingService.captureException(error, { context: 'logout_token_cleanup' });
      // This ensures storage cleanup failures don't go unnoticed in production
    }

    // Reset store state (always happens regardless of SecureStore errors)
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  },

  // CheckAuth action: validate token on app load or after app resume
  checkAuth: async () => {
    try {
      // Retrieve token from SecureStore
      const storedToken = await SecureStore.getItemAsync(AUTH_TOKEN_KEY);

      // If no token exists, mark loading as false and return early
      if (!storedToken) {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
        return;
      }

      // Token exists, validate with backend
      try {
        const response = await apiClient.get<User>('/api/v1/auth/me', {
          headers: {
            Authorization: `Bearer ${storedToken}`,
          },
        });

        // Token is valid, restore user session
        set({
          user: response.data,
          token: storedToken,
          isAuthenticated: true,
          isLoading: false,
        });
      } catch (error) {
        // Token validation failed (likely 401)
        // Delete invalid token from SecureStore
        try {
          await SecureStore.deleteItemAsync(AUTH_TOKEN_KEY);
        } catch (deleteError) {
          if (__DEV__) {
            console.error('Error deleting invalid token:', deleteError);
          }
          // Note: Consider error tracking for production deployment
        }

        // Reset to logged-out state
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });

        // Don't throw - let app proceed with logged-out state
      }
    } catch (error) {
      // Unexpected error during token retrieval (storage or network)
      if (__DEV__) {
        console.error('Error checking auth:', error);
      }

      // Note: Consider logging unexpected errors to error tracking service for investigation
      // Example: errorTrackingService.captureException(error, { context: 'checkAuth_initialization' });

      // Reset to logged-out state
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },
}));
