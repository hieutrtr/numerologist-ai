import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  SafeAreaView,
  ActivityIndicator,
  StyleSheet,
  ScrollView,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '@/stores/useAuthStore';
import { User } from '@/types/user.types';

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
  const [isLoading, setIsLoading] = useState(false);
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
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContent}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading profile...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Render error state
  if (error) {
    return (
      <SafeAreaView style={styles.container}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity
              style={styles.retryButton}
              onPress={handleRetry}
              disabled={isSubmitting}
            >
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Handle case where user data is missing
  if (!user) {
    return (
      <SafeAreaView style={styles.container}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>
              Unable to load profile data. Please try logging out and back in.
            </Text>
            <TouchableOpacity
              style={styles.retryButton}
              onPress={handleLogout}
              disabled={isSubmitting}
            >
              <Text style={styles.retryButtonText}>Logout and Login Again</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Render profile information
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Profile Card */}
        <View style={styles.profileCard}>
          <View style={styles.cardSection}>
            <Text style={styles.sectionTitle}>Profile Information</Text>
          </View>

          {/* Full Name */}
          <View style={styles.fieldContainer}>
            <Text style={styles.label}>Full Name</Text>
            <Text style={styles.value}>
              {user.full_name || 'Not provided'}
            </Text>
          </View>

          {/* Email */}
          <View style={styles.fieldContainer}>
            <Text style={styles.label}>Email Address</Text>
            <Text style={styles.value}>{user.email || 'Not provided'}</Text>
          </View>

          {/* Birth Date */}
          <View style={styles.fieldContainer}>
            <Text style={styles.label}>Birth Date</Text>
            <Text style={styles.value}>
              {getFormattedBirthDate(user.birth_date)}
            </Text>
          </View>
        </View>

        {/* Logout Button */}
        <TouchableOpacity
          style={[
            styles.logoutButton,
            isSubmitting && styles.logoutButtonDisabled,
          ]}
          onPress={handleLogout}
          disabled={isSubmitting}
          activeOpacity={isSubmitting ? 1 : 0.7}
          testID="logout-button"
        >
          {isSubmitting ? (
            <View style={styles.logoutButtonContent}>
              <ActivityIndicator size="small" color="#fff" />
              <Text style={[styles.logoutButtonText, { marginLeft: 8 }]}>
                Logging out...
              </Text>
            </View>
          ) : (
            <Text style={styles.logoutButtonText}>Logout</Text>
          )}
        </TouchableOpacity>

        {/* Footer spacing */}
        <View style={styles.footerSpacer} />
      </ScrollView>
    </SafeAreaView>
  );
}

/**
 * StyleSheet for Profile Screen
 * Uses React Native StyleSheet for performance optimization
 * Consistent with login and register screen styling
 */
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContent: {
    flexGrow: 1,
    padding: 20,
  },
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },

  // Profile Card Styles
  profileCard: {
    backgroundColor: '#f9f9f9',
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#e8e8e8',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  cardSection: {
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
  },

  // Field Styles
  fieldContainer: {
    marginBottom: 16,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
    color: '#777',
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  value: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },

  // Logout Button Styles
  logoutButton: {
    backgroundColor: '#FF3B30',
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 50,
    marginBottom: 12,
  },
  logoutButtonDisabled: {
    opacity: 0.6,
  },
  logoutButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },

  // Error Styles
  errorContainer: {
    backgroundColor: '#ffebee',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ef5350',
    marginBottom: 20,
  },
  errorText: {
    color: '#c62828',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  retryButton: {
    backgroundColor: '#c62828',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 6,
    alignItems: 'center',
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },

  // Footer Spacing
  footerSpacer: {
    height: 20,
  },
});
