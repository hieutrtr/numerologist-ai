import { create } from 'zustand';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { apiClient } from '../services/api';
import { User, RegisterData, AuthResponse, AuthState } from '../types/user.types';

const AUTH_TOKEN_KEY = 'auth_token';

/**
 * Platform-aware token storage
 * - On native (iOS/Android): Uses SecureStore for encrypted storage
 * - On web: Uses localStorage (web secure context should use HTTPS)
 */
const tokenStorage = {
  async setItem(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') {
      // On web, use localStorage (in production, use HTTPS)
      try {
        localStorage.setItem(key, value);
      } catch (error) {
        console.error('Error storing token in localStorage:', error);
        throw error;
      }
    } else {
      // On native platforms, use SecureStore
      try {
        await SecureStore.setItemAsync(key, value);
      } catch (error) {
        console.error('Error storing token in SecureStore:', error);
        throw error;
      }
    }
  },

  async getItem(key: string): Promise<string | null> {
    if (Platform.OS === 'web') {
      // On web, use localStorage
      try {
        return localStorage.getItem(key);
      } catch (error) {
        console.error('Error retrieving token from localStorage:', error);
        return null;
      }
    } else {
      // On native platforms, use SecureStore
      try {
        return await SecureStore.getItemAsync(key);
      } catch (error) {
        console.error('Error retrieving token from SecureStore:', error);
        return null;
      }
    }
  },

  async removeItem(key: string): Promise<void> {
    if (Platform.OS === 'web') {
      // On web, use localStorage
      try {
        localStorage.removeItem(key);
      } catch (error) {
        console.error('Error removing token from localStorage:', error);
        throw error;
      }
    } else {
      // On native platforms, use SecureStore
      try {
        await SecureStore.deleteItemAsync(key);
      } catch (error) {
        console.error('Error removing token from SecureStore:', error);
        throw error;
      }
    }
  },
};

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

      // Store token (platform-aware: SecureStore on native, localStorage on web)
      await tokenStorage.setItem(AUTH_TOKEN_KEY, access_token);

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

      // Store token (platform-aware: SecureStore on native, localStorage on web)
      await tokenStorage.setItem(AUTH_TOKEN_KEY, access_token);

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
      // Delete token (platform-aware: SecureStore on native, localStorage on web)
      await tokenStorage.removeItem(AUTH_TOKEN_KEY);
    } catch (error) {
      // Log error but don't throw - logout should always succeed
      if (__DEV__) {
        console.error('Error deleting token from storage:', error);
      }

      // In production, consider sending to error tracking service (e.g., Sentry)
      // Example: errorTrackingService.captureException(error, { context: 'logout_token_cleanup' });
      // This ensures storage cleanup failures don't go unnoticed in production
    }

    // Reset store state (always happens regardless of storage errors)
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
      // Retrieve token (platform-aware: SecureStore on native, localStorage on web)
      const storedToken = await tokenStorage.getItem(AUTH_TOKEN_KEY);

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
        // Delete invalid token from storage
        try {
          await tokenStorage.removeItem(AUTH_TOKEN_KEY);
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

  // Google Sign-In action: authenticate with Google OAuth ID token
  googleSignIn: async (idToken: string) => {
    try {
      set({ isLoading: true });

      // Send Google ID token to backend for verification and user creation/linking
      // Backend handles three cases:
      // 1. New user: Creates User + OAuthAccount
      // 2. Existing OAuth user: Returns existing user
      // 3. Email match: Links OAuthAccount to existing password user
      const response = await apiClient.post<AuthResponse>('/api/v1/auth/google', {
        id_token: idToken,
      });

      const { user, access_token } = response.data;

      // Store token (platform-aware: SecureStore on native, localStorage on web)
      await tokenStorage.setItem(AUTH_TOKEN_KEY, access_token);

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
}));
