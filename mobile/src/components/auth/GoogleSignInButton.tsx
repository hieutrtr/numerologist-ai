/**
 * Google Sign-In Button Component
 *
 * Renders a Google Sign-In button that triggers the OAuth flow.
 * Handles the complete Google authentication process and returns the ID token
 * to the parent component for backend verification.
 *
 * Features:
 * - Triggers Google OAuth flow via Google Sign-In SDK
 * - Handles loading and error states
 * - Cross-platform support (Android primary, iOS and Web with limitations)
 * - Graceful error handling with user-friendly messages
 * - Follows design consistency with existing auth screens
 */

import React, { useEffect, useState } from 'react';
import {
  TouchableOpacity,
  Text,
  View,
  ActivityIndicator,
  StyleSheet,
  Platform,
  Alert,
} from 'react-native';
import { GoogleSignin, statusCodes } from '@react-native-google-signin/google-signin';
import { useAuthStore } from '@/stores/useAuthStore';
import { MaterialIcons } from '@expo/vector-icons';

interface GoogleSignInButtonProps {
  /**
   * Callback when sign-in succeeds
   * @param idToken - Google ID token to send to backend
   */
  onSuccess?: (idToken: string) => void;

  /**
   * Callback when sign-in fails
   * @param error - Error message
   */
  onError?: (error: string) => void;

  /**
   * Optional custom text for the button (default: "Sign in with Google")
   */
  buttonText?: string;

  /**
   * Whether the button is disabled (useful while request is in flight)
   */
  disabled?: boolean;
}

/**
 * Google Sign-In Button Component
 *
 * Manages Google OAuth sign-in flow with error handling and loading states.
 * Must be wrapped with GoogleSignInProvider in app root layout.
 *
 * Usage:
 * ```tsx
 * <GoogleSignInButton
 *   onSuccess={(idToken) => handleGoogleSignIn(idToken)}
 *   onError={(error) => showError(error)}
 * />
 * ```
 */
export function GoogleSignInButton({
  onSuccess,
  onError,
  buttonText = 'Sign in with Google',
  disabled = false,
}: GoogleSignInButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const { googleSignIn } = useAuthStore();

  /**
   * Initialize Google Sign-In SDK on component mount
   * Configure with Web Client ID from environment
   */
  useEffect(() => {
    const initializeGoogleSignIn = async () => {
      try {
        await GoogleSignin.hasPlayServices();

        // Configure Google Sign-In with Web Client ID
        GoogleSignin.configure({
          webClientId: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID || '',
          // For Android, also include Android client ID from native build
          // androidClientId is handled in google-services.json
          offlineAccess: false, // We don't need offline access for this flow
          forceCodeForRefreshToken: false,
        });

        setIsInitialized(true);
      } catch (error: any) {
        console.error('Google Sign-In initialization failed:', error);
        setIsInitialized(false);

        // On web, initialization might fail but we should still allow trying
        if (Platform.OS === 'web') {
          setIsInitialized(true);
        }
      }
    };

    initializeGoogleSignIn();
  }, []);

  /**
   * Handle Google Sign-In button press
   * Triggers OAuth flow and retrieves ID token
   */
  const handleGoogleSignIn = async () => {
    if (!isInitialized || isLoading || disabled) {
      return;
    }

    setIsLoading(true);

    try {
      // Trigger Google Sign-In flow
      const response = await GoogleSignin.signIn();

      // Get the ID token from the response
      const idToken = response.idToken;

      if (!idToken) {
        throw new Error('No ID token in Google Sign-In response');
      }

      // Call the auth store's googleSignIn method to verify token and login
      // This handles creating/linking user in the backend
      await googleSignIn(idToken);

      // Notify parent component of successful sign-in
      onSuccess?.(idToken);
    } catch (error: any) {
      // Handle specific error codes
      let errorMessage = 'Google Sign-In failed';

      if (error.code === statusCodes.SIGN_IN_CANCELLED) {
        errorMessage = 'Sign-in was cancelled';
      } else if (error.code === statusCodes.IN_PROGRESS) {
        errorMessage = 'Sign-in is already in progress';
      } else if (error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
        errorMessage = 'Google Play Services not available';
      } else if (error.message) {
        errorMessage = error.message;
      }

      console.error('Google Sign-In error:', error);

      // Show error to user
      onError?.(errorMessage);

      // Also show alert for better visibility
      if (Platform.OS !== 'web') {
        Alert.alert('Sign-In Failed', errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Don't render if not initialized
  if (!isInitialized) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="small" color="#1f2937" />
        <Text style={styles.loadingText}>Setting up Google Sign-In...</Text>
      </View>
    );
  }

  return (
    <TouchableOpacity
      style={[
        styles.button,
        (disabled || isLoading) && styles.buttonDisabled,
      ]}
      onPress={handleGoogleSignIn}
      disabled={disabled || isLoading}
      activeOpacity={disabled || isLoading ? 1 : 0.7}
    >
      {isLoading ? (
        <View style={styles.buttonContent}>
          <ActivityIndicator size="small" color="#fff" />
          <Text style={[styles.buttonText, { marginLeft: 8 }]}>Signing in...</Text>
        </View>
      ) : (
        <View style={styles.buttonContent}>
          <MaterialIcons name="account-circle" size={20} color="#1f2937" />
          <Text style={styles.buttonText}>{buttonText}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

/**
 * StyleSheet for Google Sign-In Button
 * Maintains consistency with existing login/register screen styling
 */
const styles = StyleSheet.create({
  button: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e5e7eb',
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 50,
    marginVertical: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 1,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#1f2937',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  loadingContainer: {
    paddingVertical: 14,
    paddingHorizontal: 20,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 50,
    marginVertical: 12,
  },
  loadingText: {
    marginTop: 8,
    fontSize: 14,
    color: '#666',
  },
});

export default GoogleSignInButton;
