import { Stack } from 'expo-router';

/**
 * Auth Stack Layout
 *
 * Manages navigation for authentication-related screens (login, register)
 * Uses route grouping (auth) to hide "auth" prefix from URL paths
 * Routes: /login, /register (not /auth/login, /auth/register)
 */
export default function AuthLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false, // Hide headers for auth screens
      }}
    />
  );
}
