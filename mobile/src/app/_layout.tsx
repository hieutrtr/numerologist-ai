import React, { useEffect } from 'react';
import { Stack, useRouter, useSegments } from 'expo-router';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useAuthStore } from '@/stores/useAuthStore';

/**
 * Root Layout Component
 *
 * Handles authentication state and routing based on auth status.
 * - Shows loading screen while checking auth state
 * - Redirects to login if not authenticated
 * - Redirects to tabs/home if authenticated
 */
export default function RootLayout() {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const segments = useSegments();
  const router = useRouter();

  // Check authentication on app load
  useEffect(() => {
    checkAuth();
  }, []);

  // Handle authentication-based routing
  useEffect(() => {
    if (isLoading) return; // Don't redirect while loading

    const inAuthGroup = segments[0] === '(auth)';
    const inTabsGroup = segments[0] === '(tabs)' || segments.length === 0;

    if (__DEV__) {
      console.log('🚦 Root layout navigation check:', {
        isAuthenticated,
        isLoading,
        currentSegments: segments,
        inAuthGroup,
        inTabsGroup,
      });
    }

    if (!isAuthenticated && !inAuthGroup) {
      // Not authenticated and not in auth screens - redirect to login
      router.replace('/(auth)/login');
    } else if (isAuthenticated && inAuthGroup) {
      // Authenticated but still in auth screens - redirect to home
      router.replace('/');
    }
  }, [isAuthenticated, isLoading, segments]);

  // Show loading screen while checking auth
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <Stack
      screenOptions={{
        headerShown: false,
      }}
    />
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
});
