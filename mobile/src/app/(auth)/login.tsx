import React, { useRef, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Keyboard,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Link } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';
import { useAuthStore } from '@/stores/useAuthStore';
import { GoogleSignInButton } from '@/components/auth/GoogleSignInButton';

/**
 * Login Screen Component
 *
 * Provides user authentication interface with email/password form.
 * Features:
 * - Email and password input fields with validation
 * - Show/hide password toggle
 * - Loading state while authenticating
 * - Error message display
 * - Keyboard handling (next/done buttons)
 * - Cross-platform support (web, iOS, Android)
 * - Navigation to register screen
 *
 * Integration:
 * - Uses useAuthStore for authentication logic
 * - Uses expo-router for navigation
 */
export default function LoginScreen() {
  // State management
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Refs for keyboard navigation
  const passwordInputRef = useRef<TextInput>(null);

  // Auth store and router
  const { login } = useAuthStore();

  /**
   * Email validation using regex pattern
   * Validates basic email format: something@something.something
   */
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  /**
   * Handle email input change - clear errors when user types
   */
  const handleEmailChange = (text: string) => {
    setEmail(text);
    // Clear errors when user starts editing
    if (error) {
      setError(null);
    }
  };

  /**
   * Handle password input change - clear errors when user types
   */
  const handlePasswordChange = (text: string) => {
    setPassword(text);
    // Clear errors when user starts editing
    if (error) {
      setError(null);
    }
  };

  /**
   * Main login handler
   *
   * Flow:
   * 1. Clear previous errors
   * 2. Validate email format
   * 3. Call auth store login
   * 4. On success, navigate to home with replace (prevents back navigation)
   * 5. On error, display user-friendly message
   */
  const handleLogin = async () => {
    try {
      // Clear previous errors
      setError(null);

      // Dismiss keyboard
      Keyboard.dismiss();

      // Validate email format
      if (!email.trim()) {
        setError('Please enter your email address');
        return;
      }

      if (!validateEmail(email)) {
        setError('Please enter a valid email address');
        return;
      }

      if (!password) {
        setError('Please enter your password');
        return;
      }

      // Set submitting state for this login attempt
      setIsSubmitting(true);

      // Call auth store login method
      await login(email, password);

      // Navigation is handled automatically by root layout based on auth state
      // No need to manually navigate - the root layout will detect isAuthenticated=true
      // and redirect to home automatically
    } catch (err: any) {
      // Display user-friendly error messages
      let errorMessage = 'Login failed. Please try again.';

      // Extract error message from API response
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message === 'Network Error') {
        errorMessage = 'Network error. Please check your connection.';
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      setIsSubmitting(false);
    }
  };

  /**
   * Determine if login button should be disabled
   * Disabled when submitting or required fields are empty
   */
  const isLoginDisabled = !email.trim() || !password || isSubmitting;

  return (
    <SafeAreaView className="flex-1 bg-dark">
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1 justify-center"
      >
        <View className="px-lg py-lg">
          {/* Header */}
          <View className="mb-xxl items-center">
            <Text className="text-display font-bold text-text-primary mb-sm">Welcome Back</Text>
            <Text className="text-body text-text-secondary font-normal">Sign in to your account</Text>
          </View>

          {/* Error Message Display */}
          {error && (
            <View className="bg-error/20 border border-error rounded-lg p-md mb-lg">
              <Text className="text-small text-error font-semibold">{error}</Text>
            </View>
          )}

          {/* Form Fields */}
          <View className="mb-lg">
            {/* Email Input */}
            <View className="mb-md">
              <Text className="text-small font-semibold text-text-primary mb-xs">Email</Text>
              <TextInput
                className={`border rounded-lg px-md py-md text-body font-normal text-text-primary ${
                  error ? 'border-error bg-error/10' : 'border-border bg-light'
                }`}
                placeholder="your@email.com"
                placeholderTextColor="#6b7280"
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
                editable={!isSubmitting}
                returnKeyType="next"
                onChangeText={handleEmailChange}
                onSubmitEditing={() => passwordInputRef.current?.focus()}
                value={email}
                testID="email-input"
              />
            </View>

            {/* Password Input with Show/Hide Toggle */}
            <View className="mb-md">
              <Text className="text-small font-semibold text-text-primary mb-xs">Password</Text>
              <View className="flex-row items-center relative">
                <TextInput
                  ref={passwordInputRef}
                  className={`flex-1 border rounded-lg px-md py-md text-body font-normal text-text-primary ${
                    error ? 'border-error bg-error/10' : 'border-border bg-light'
                  }`}
                  placeholder="••••••••"
                  placeholderTextColor="#6b7280"
                  secureTextEntry={!showPassword}
                  editable={!isSubmitting}
                  returnKeyType="done"
                  onChangeText={handlePasswordChange}
                  onSubmitEditing={handleLogin}
                  value={password}
                  testID="password-input"
                />
                <TouchableOpacity
                  className="absolute right-md py-md px-sm"
                  onPress={() => setShowPassword(!showPassword)}
                  testID="toggle-password"
                >
                  <MaterialIcons
                    name={showPassword ? 'visibility' : 'visibility-off'}
                    size={20}
                    color="#6b7280"
                  />
                </TouchableOpacity>
              </View>
            </View>
          </View>

          {/* Login Button */}
          <TouchableOpacity
            className={`bg-primary rounded-lg py-sm px-md items-center justify-center mb-lg min-h-[50px] ${
              isLoginDisabled ? 'opacity-60' : ''
            }`}
            onPress={handleLogin}
            disabled={isLoginDisabled}
            testID="login-button"
          >
            {isSubmitting ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <Text className="text-body font-semibold text-white">Login</Text>
            )}
          </TouchableOpacity>

          {/* Divider */}
          <View className="flex-row items-center my-lg">
            <View className="flex-1 h-px bg-border" />
            <Text className="mx-md text-small text-text-muted font-semibold">or</Text>
            <View className="flex-1 h-px bg-border" />
          </View>

          {/* Google Sign-In Button */}
          <GoogleSignInButton />

          {/* Register Link */}
          <View className="flex-row justify-center items-center py-sm">
            <Text className="text-small text-text-secondary">Don't have an account? </Text>
            <Link href="/(auth)/register" asChild>
              <TouchableOpacity testID="register-link">
                <Text className="text-small text-primary font-semibold">Register</Text>
              </TouchableOpacity>
            </Link>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
