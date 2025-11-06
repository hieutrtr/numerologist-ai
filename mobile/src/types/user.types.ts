/**
 * User-related TypeScript types for authentication and user management
 * Matches backend UserResponse schema from backend/src/schemas/user.py
 */

/**
 * User interface matching the backend UserResponse schema
 * Excludes hashed_password for security
 */
export interface User {
  id: string; // UUID from backend
  email: string;
  full_name: string;
  birth_date: string; // ISO date format (YYYY-MM-DD)
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

/**
 * Registration credentials required to create a new user account
 */
export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  birth_date: string; // ISO date format (YYYY-MM-DD)
}

/**
 * Login credentials for authentication
 */
export interface LoginCredentials {
  email: string;
  password: string;
}

/**
 * Backend API response for login/register endpoints
 * Contains user data and JWT access token
 */
export interface AuthResponse {
  user: User;
  access_token: string;
}

/**
 * Auth store state and actions
 * Manages user authentication state and token persistence
 */
export interface AuthState {
  // State
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  googleSignIn: (idToken: string) => Promise<void>;
}
