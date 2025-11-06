import React, { useRef, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  StyleSheet,
  Keyboard,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Link } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';
import { useAuthStore } from '@/stores/useAuthStore';

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
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <View style={styles.content}>
          {/* Header */}
          <View style={styles.headerContainer}>
            <Text style={styles.title}>Welcome Back</Text>
            <Text style={styles.subtitle}>Sign in to your account</Text>
          </View>

          {/* Error Message Display */}
          {error && (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}

          {/* Form Fields */}
          <View style={styles.formContainer}>
            {/* Email Input */}
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Email</Text>
              <TextInput
                style={[styles.input, error && styles.inputError]}
                placeholder="your@email.com"
                placeholderTextColor="#999"
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
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Password</Text>
              <View style={styles.passwordContainer}>
                <TextInput
                  ref={passwordInputRef}
                  style={[styles.input, styles.passwordInput, error && styles.inputError]}
                  placeholder="••••••••"
                  placeholderTextColor="#999"
                  secureTextEntry={!showPassword}
                  editable={!isSubmitting}
                  returnKeyType="done"
                  onChangeText={handlePasswordChange}
                  onSubmitEditing={handleLogin}
                  value={password}
                  testID="password-input"
                />
                <TouchableOpacity
                  style={styles.toggleButton}
                  onPress={() => setShowPassword(!showPassword)}
                  testID="toggle-password"
                >
                  <MaterialIcons
                    name={showPassword ? 'visibility' : 'visibility-off'}
                    size={20}
                    color="#666"
                  />
                </TouchableOpacity>
              </View>
            </View>
          </View>

          {/* Login Button */}
          <TouchableOpacity
            style={[styles.loginButton, isLoginDisabled && styles.loginButtonDisabled]}
            onPress={handleLogin}
            disabled={isLoginDisabled}
            testID="login-button"
          >
            {isSubmitting ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <Text style={styles.loginButtonText}>Login</Text>
            )}
          </TouchableOpacity>

          {/* Register Link */}
          <View style={styles.registerContainer}>
            <Text style={styles.registerText}>Don't have an account? </Text>
            <Link href="/(auth)/register" asChild>
              <TouchableOpacity testID="register-link">
                <Text style={styles.registerLink}>Register</Text>
              </TouchableOpacity>
            </Link>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

/**
 * React Native StyleSheet
 * Provides performant styling with platform-specific optimizations
 */
const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#fff',
  },
  container: {
    flex: 1,
    justifyContent: 'center',
  },
  content: {
    paddingHorizontal: 20,
    paddingVertical: 24,
  },
  headerContainer: {
    marginBottom: 32,
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#000',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    fontWeight: '400',
  },
  errorContainer: {
    backgroundColor: '#FFE5E5',
    borderWidth: 1,
    borderColor: '#FF3B30',
    borderRadius: 8,
    padding: 12,
    marginBottom: 20,
  },
  errorText: {
    color: '#FF3B30',
    fontSize: 14,
    fontWeight: '500',
  },
  formContainer: {
    marginBottom: 24,
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#000',
    marginBottom: 6,
  },
  input: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 14,
    color: '#000',
    backgroundColor: '#f9f9f9',
  },
  inputError: {
    borderColor: '#FF3B30',
    backgroundColor: '#FFEDED',
  },
  passwordContainer: {
    position: 'relative',
    flexDirection: 'row',
    alignItems: 'center',
  },
  passwordInput: {
    flex: 1,
  },
  toggleButton: {
    position: 'absolute',
    right: 12,
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  loginButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 14,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
    minHeight: 50,
  },
  loginButtonDisabled: {
    opacity: 0.6,
  },
  loginButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  registerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 8,
  },
  registerText: {
    fontSize: 14,
    color: '#666',
  },
  registerLink: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
});
