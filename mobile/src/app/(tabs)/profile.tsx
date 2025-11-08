import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useAuthStore } from '@/stores/useAuthStore';

/**
 * Profile Screen Component
 *
 * Displays authenticated user's profile information including:
 * - Full name
 * - Email address
 * - Birth date (formatted as readable date)
 * - Logout button for signing out
 *
 * Features:
 * - Loading state while user data is being retrieved
 * - Error handling with retry capability
 * - Graceful handling of missing user data
 * - Logout with automatic navigation to login screen
 * - Cross-platform support (Web, iOS, Android)
 * - Responsive layout with SafeAreaView for mobile notch avoidance
 */
export default function ProfileScreen() {
  // State management
  const [isLoading] = useState(false); // Currently not used, reserved for future data fetching
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Auth store and router
  const { user, logout } = useAuthStore();
  const router = useRouter();

  /**
   * Format birth date from ISO string to readable format
   * Example: "1990-05-15" → "May 15, 1990"
   * Uses native JavaScript Intl.DateTimeFormat for cross-platform compatibility
   */
  const getFormattedBirthDate = (birthDateStr: string): string => {
    try {
      // Handle both ISO string formats and edge cases
      if (!birthDateStr) return 'Not available';

      // Parse ISO date string to Date object
      const date = new Date(birthDateStr);

      // Check for invalid date
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }

      // Format using native Intl.DateTimeFormat (no external dependency)
      // Works cross-platform: Web, iOS, Android
      const formatter = new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
      return formatter.format(date);
    } catch (err) {
      return 'Error formatting date';
    }
  };

  /**
   * Handle logout action
   */
  const handleLogout = async () => {
    try {
      setError(null);
      setIsSubmitting(true);

      // Call logout from auth store
      await logout();

      // Navigate to login screen after logout
      // Use router.replace() to prevent back navigation
      router.replace('/(auth)/login');
    } catch (err: any) {
      // Handle logout errors gracefully
      const errorMessage = err?.message || 'Logout failed. Please try again.';
      setError(errorMessage);
      setIsSubmitting(false);
    }
  };

  /**
   * Handle retry for error states
   */
  const handleRetry = () => {
    setError(null);
    // User data is already loaded from auth store
    // No additional fetch needed - just clear error state
  };

  // Render loading state
  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 bg-dark">
        <View className="flex-1 justify-center items-center p-lg">
          <ActivityIndicator size="large" color="#d4af37" />
          <Text className="text-body text-text-muted mt-md text-center">Loading profile...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Render error state
  if (error) {
    return (
      <SafeAreaView className="flex-1 bg-dark">
        <ScrollView
          contentContainerStyle={{ flexGrow: 1 }}
          showsVerticalScrollIndicator={false}
        >
          <View className="flex-1 p-lg">
            <View className="bg-error/20 border border-error rounded-lg p-md mb-lg">
              <Text className="text-error font-semibold mb-md">{error}</Text>
              <TouchableOpacity
                className="bg-error rounded-lg px-md py-sm items-center"
                onPress={handleRetry}
                disabled={isSubmitting}
              >
                <Text className="text-white font-semibold text-small">Retry</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Handle case where user data is missing
  if (!user) {
    return (
      <SafeAreaView className="flex-1 bg-dark">
        <ScrollView
          contentContainerStyle={{ flexGrow: 1 }}
          showsVerticalScrollIndicator={false}
        >
          <View className="flex-1 p-lg">
            <View className="bg-error/20 border border-error rounded-lg p-md mb-lg">
              <Text className="text-error font-semibold mb-md">
                Unable to load profile data. Please try logging out and back in.
              </Text>
              <TouchableOpacity
                className="bg-error rounded-lg px-md py-sm items-center"
                onPress={handleLogout}
                disabled={isSubmitting}
              >
                <Text className="text-white font-semibold text-small">Logout and Login Again</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Render profile information
  return (
    <SafeAreaView className="flex-1 bg-dark">
      <ScrollView
        contentContainerStyle={{ flexGrow: 1 }}
        showsVerticalScrollIndicator={false}
      >
        <View className="flex-1 p-lg">
          {/* Profile Card */}
          <View className="bg-card rounded-lg p-lg mb-xxl border border-border">
            <View className="pb-md mb-md border-b border-border">
              <Text className="text-h1 font-bold text-text-primary">Profile Information</Text>
            </View>

            {/* Full Name */}
            <View className="mb-md">
              <Text className="text-tiny font-semibold text-text-muted uppercase mb-xs">Full Name</Text>
              <Text className="text-body font-medium text-text-primary">
                {user.full_name || 'Not provided'}
              </Text>
            </View>

            {/* Email */}
            <View className="mb-md">
              <Text className="text-tiny font-semibold text-text-muted uppercase mb-xs">Email Address</Text>
              <Text className="text-body font-medium text-text-primary">{user.email || 'Not provided'}</Text>
            </View>

            {/* Birth Date */}
            <View className="mb-md">
              <Text className="text-tiny font-semibold text-text-muted uppercase mb-xs">Birth Date</Text>
              <Text className="text-body font-medium text-text-primary">
                {getFormattedBirthDate(user.birth_date)}
              </Text>
            </View>
          </View>

          {/* Logout Button */}
          <TouchableOpacity
            className={`bg-error rounded-lg py-sm px-md items-center justify-center min-h-[50px] mb-sm ${
              isSubmitting ? 'opacity-60' : ''
            }`}
            onPress={handleLogout}
            disabled={isSubmitting}
            activeOpacity={isSubmitting ? 1 : 0.7}
            testID="logout-button"
          >
            {isSubmitting ? (
              <View className="flex-row items-center justify-center">
                <ActivityIndicator size="small" color="#fff" />
                <Text className="text-body font-semibold text-white ml-md">
                  Logging out...
                </Text>
              </View>
            ) : (
              <Text className="text-body font-semibold text-white">Logout</Text>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

