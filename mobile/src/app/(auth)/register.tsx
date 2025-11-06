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
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Link, useRouter } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';
import DateTimePicker from '@react-native-community/datetimepicker';
import { useAuthStore } from '@/stores/useAuthStore';

/**
 * Register Screen Component
 *
 * Provides user account creation interface with comprehensive form validation.
 * Features:
 * - Email, password, confirm password, full name, and birth date input fields
 * - Form validation with inline error messages
 * - Show/hide password toggles for both password fields
 * - Native date picker on mobile, HTML date input on web
 * - Loading state while registering
 * - Error message display
 * - Keyboard handling (next/done buttons)
 * - Cross-platform support (web, iOS, Android)
 * - Navigation to login screen
 *
 * Integration:
 * - Uses useAuthStore for registration logic
 * - Uses expo-router for navigation
 * - Uses @react-native-community/datetimepicker for date selection
 */
export default function RegisterScreen() {
  // Form state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [birthDate, setBirthDate] = useState<Date | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // UI state
  const [error, setError] = useState<string | null>(null);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Refs for keyboard navigation
  const emailInputRef = useRef<TextInput>(null);
  const passwordInputRef = useRef<TextInput>(null);
  const confirmPasswordInputRef = useRef<TextInput>(null);

  // Auth store and router
  const { register } = useAuthStore();
  const router = useRouter();

  /**
   * Email validation using regex pattern
   * Validates basic email format: something@something.something
   */
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  /**
   * Password validation - minimum 8 characters
   */
  const validatePassword = (password: string): boolean => {
    return password.length >= 8;
  };

  /**
   * Password confirmation validation - must match password
   */
  const validatePasswordMatch = (
    password: string,
    confirmPassword: string
  ): boolean => {
    return password === confirmPassword;
  };

  /**
   * Full name validation - not empty after trimming
   */
  const validateFullName = (name: string): boolean => {
    return name.trim().length > 0;
  };

  /**
   * Birth date validation - valid date, not in future
   */
  const validateBirthDate = (date: Date | null): boolean => {
    if (!date) return false;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date <= today;
  };

  /**
   * Comprehensive form validation
   * Returns true if all validations pass, false otherwise
   */
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Validate full name
    if (!validateFullName(fullName)) {
      newErrors.fullName = 'Full name is required';
    }

    // Validate email
    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(email)) {
      newErrors.email = 'Invalid email format';
    }

    // Validate password
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (!validatePassword(password)) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    // Validate password confirmation
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (!validatePasswordMatch(password, confirmPassword)) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Validate birth date
    if (!validateBirthDate(birthDate)) {
      newErrors.birthDate = 'Valid birth date is required (not in the future)';
    }

    setFieldErrors(newErrors);

    if (Object.keys(newErrors).length > 0) {
      setError('Please fix the errors below');
      return false;
    }

    return true;
  };

  /**
   * Handle field changes - clear errors for that specific field
   */
  const handleFieldChange = (
    value: string,
    fieldName: string,
    setter: (value: string) => void
  ) => {
    setter(value);
    // Clear field-specific error when user starts editing
    if (fieldErrors[fieldName]) {
      const newErrors = { ...fieldErrors };
      delete newErrors[fieldName];
      setFieldErrors(newErrors);
    }
    // Clear general error
    if (error) {
      setError(null);
    }
  };

  /**
   * Format birth date for display
   */
  const formatBirthDate = (date: Date | null): string => {
    if (!date) return 'Select Birth Date';
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  /**
   * Handle date picker change - mobile and web
   */
  const handleDateChange = (_event: any, selectedDate?: Date) => {
    if (Platform.OS !== 'web') {
      setShowDatePicker(false);
    }

    if (selectedDate) {
      setBirthDate(selectedDate);
      // Clear field error when user selects a date
      if (fieldErrors.birthDate) {
        const newErrors = { ...fieldErrors };
        delete newErrors.birthDate;
        setFieldErrors(newErrors);
      }
    }
  };

  /**
   * Main registration handler
   *
   * Flow:
   * 1. Clear previous errors
   * 2. Validate form
   * 3. Set submitting state
   * 4. Format birth date as ISO string (YYYY-MM-DD)
   * 5. Call auth store register
   * 6. On success, navigate to home with replace (prevents back navigation)
   * 7. On error, display user-friendly message and reset submitting state
   */
  const handleRegister = async () => {
    try {
      // Clear previous errors
      setError(null);
      setFieldErrors({});

      // Dismiss keyboard
      Keyboard.dismiss();

      // Validate form
      if (!validateForm()) {
        return;
      }

      // Set submitting state for this registration attempt
      setIsSubmitting(true);

      // Format birth date for API (ISO 8601: YYYY-MM-DD)
      const birthDateISO = birthDate!.toISOString().split('T')[0];

      // Call auth store register method with RegisterData object
      await register({
        email,
        password,
        full_name: fullName,
        birth_date: birthDateISO,
      });

      // Navigate to home screen on success
      // Use replace() instead of push() to prevent going back to register
      router.replace('/');
    } catch (err: any) {
      // Display user-friendly error messages
      let errorMessage = 'Registration failed. Please try again.';

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
   * Determine if register button should be disabled
   * Disabled when submitting or any required field is empty
   */
  const isRegisterDisabled =
    !fullName.trim() ||
    !email.trim() ||
    !password ||
    !confirmPassword ||
    !birthDate ||
    isSubmitting;

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.content}>
            {/* Header */}
            <View style={styles.headerContainer}>
              <Text style={styles.title}>Create Account</Text>
              <Text style={styles.subtitle}>Join us to start your journey</Text>
            </View>

            {/* Error Message Display */}
            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            {/* Form Fields */}
            <View style={styles.formContainer}>
              {/* Full Name Input */}
              <View style={styles.inputGroup}>
                <Text style={styles.label}>Full Name</Text>
                <TextInput
                  style={[
                    styles.input,
                    fieldErrors.fullName && styles.inputError,
                  ]}
                  placeholder="John Doe"
                  placeholderTextColor="#999"
                  autoCapitalize="words"
                  autoComplete="name"
                  editable={!isSubmitting}
                  returnKeyType="next"
                  onChangeText={(text) =>
                    handleFieldChange(text, 'fullName', setFullName)
                  }
                  onSubmitEditing={() => emailInputRef.current?.focus()}
                  value={fullName}
                  testID="fullname-input"
                />
                {fieldErrors.fullName && (
                  <Text style={styles.fieldErrorText}>{fieldErrors.fullName}</Text>
                )}
              </View>

              {/* Email Input */}
              <View style={styles.inputGroup}>
                <Text style={styles.label}>Email</Text>
                <TextInput
                  ref={emailInputRef}
                  style={[styles.input, fieldErrors.email && styles.inputError]}
                  placeholder="your@email.com"
                  placeholderTextColor="#999"
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoComplete="email"
                  editable={!isSubmitting}
                  returnKeyType="next"
                  onChangeText={(text) =>
                    handleFieldChange(text, 'email', setEmail)
                  }
                  onSubmitEditing={() => passwordInputRef.current?.focus()}
                  value={email}
                  testID="email-input"
                />
                {fieldErrors.email && (
                  <Text style={styles.fieldErrorText}>{fieldErrors.email}</Text>
                )}
              </View>

              {/* Password Input with Show/Hide Toggle */}
              <View style={styles.inputGroup}>
                <Text style={styles.label}>Password</Text>
                <View style={styles.passwordContainer}>
                  <TextInput
                    ref={passwordInputRef}
                    style={[
                      styles.input,
                      styles.passwordInput,
                      fieldErrors.password && styles.inputError,
                    ]}
                    placeholder="••••••••"
                    placeholderTextColor="#999"
                    secureTextEntry={!showPassword}
                    editable={!isSubmitting}
                    returnKeyType="next"
                    onChangeText={(text) =>
                      handleFieldChange(text, 'password', setPassword)
                    }
                    onSubmitEditing={() =>
                      confirmPasswordInputRef.current?.focus()
                    }
                    value={password}
                    testID="password-input"
                  />
                  <TouchableOpacity
                    style={styles.toggleButton}
                    onPress={() => setShowPassword(!showPassword)}
                    disabled={isSubmitting}
                    testID="toggle-password"
                  >
                    <MaterialIcons
                      name={showPassword ? 'visibility' : 'visibility-off'}
                      size={20}
                      color="#666"
                    />
                  </TouchableOpacity>
                </View>
                {fieldErrors.password && (
                  <Text style={styles.fieldErrorText}>
                    {fieldErrors.password}
                  </Text>
                )}
              </View>

              {/* Confirm Password Input with Show/Hide Toggle */}
              <View style={styles.inputGroup}>
                <Text style={styles.label}>Confirm Password</Text>
                <View style={styles.passwordContainer}>
                  <TextInput
                    ref={confirmPasswordInputRef}
                    style={[
                      styles.input,
                      styles.passwordInput,
                      fieldErrors.confirmPassword && styles.inputError,
                    ]}
                    placeholder="••••••••"
                    placeholderTextColor="#999"
                    secureTextEntry={!showConfirmPassword}
                    editable={!isSubmitting}
                    returnKeyType="done"
                    onChangeText={(text) =>
                      handleFieldChange(
                        text,
                        'confirmPassword',
                        setConfirmPassword
                      )
                    }
                    onSubmitEditing={handleRegister}
                    value={confirmPassword}
                    testID="confirm-password-input"
                  />
                  <TouchableOpacity
                    style={styles.toggleButton}
                    onPress={() =>
                      setShowConfirmPassword(!showConfirmPassword)
                    }
                    disabled={isSubmitting}
                    testID="toggle-confirm-password"
                  >
                    <MaterialIcons
                      name={showConfirmPassword ? 'visibility' : 'visibility-off'}
                      size={20}
                      color="#666"
                    />
                  </TouchableOpacity>
                </View>
                {fieldErrors.confirmPassword && (
                  <Text style={styles.fieldErrorText}>
                    {fieldErrors.confirmPassword}
                  </Text>
                )}
              </View>

              {/* Birth Date Input */}
              <View style={styles.inputGroup}>
                <Text style={styles.label}>Birth Date</Text>
                {Platform.OS === 'web' ? (
                  // Web: HTML date input
                  <View style={styles.webDateInputWrapper}>
                    <input
                      type="date"
                      max={new Date().toISOString().split('T')[0]}
                      value={
                        birthDate
                          ? birthDate.toISOString().split('T')[0]
                          : ''
                      }
                      onChange={(e) => {
                        if (e.target.value) {
                          setBirthDate(new Date(e.target.value));
                          if (fieldErrors.birthDate) {
                            const newErrors = { ...fieldErrors };
                            delete newErrors.birthDate;
                            setFieldErrors(newErrors);
                          }
                        }
                      }}
                      style={styles.webDateInput}
                      disabled={isSubmitting}
                    />
                  </View>
                ) : (
                  // Mobile: Touchable button with date picker modal
                  <>
                    <TouchableOpacity
                      style={[
                        styles.dateButton,
                        fieldErrors.birthDate && styles.inputError,
                      ]}
                      onPress={() => setShowDatePicker(true)}
                      disabled={isSubmitting}
                      testID="birthdate-button"
                    >
                      <Text
                        style={[
                          styles.dateButtonText,
                          !birthDate && styles.dateButtonPlaceholder,
                        ]}
                      >
                        {formatBirthDate(birthDate)}
                      </Text>
                    </TouchableOpacity>

                    {showDatePicker && (
                      <DateTimePicker
                        value={birthDate || new Date()}
                        mode="date"
                        display="default"
                        maximumDate={new Date()}
                        onChange={handleDateChange}
                        testID="date-time-picker"
                      />
                    )}
                  </>
                )}
                {fieldErrors.birthDate && (
                  <Text style={styles.fieldErrorText}>
                    {fieldErrors.birthDate}
                  </Text>
                )}
              </View>
            </View>

            {/* Register Button */}
            <TouchableOpacity
              style={[
                styles.registerButton,
                isRegisterDisabled && styles.registerButtonDisabled,
              ]}
              onPress={handleRegister}
              disabled={isRegisterDisabled}
              testID="register-button"
            >
              {isSubmitting ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <Text style={styles.registerButtonText}>Register</Text>
              )}
            </TouchableOpacity>

            {/* Login Link */}
            <View style={styles.loginContainer}>
              <Text style={styles.loginText}>Already have an account? </Text>
              <Link href="/(auth)/login" asChild>
                <TouchableOpacity testID="login-link">
                  <Text style={styles.loginLink}>Login</Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>
        </ScrollView>
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
  },
  scrollContent: {
    flexGrow: 1,
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
  fieldErrorText: {
    color: '#FF3B30',
    fontSize: 12,
    marginTop: 4,
    fontWeight: '500',
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
  dateButton: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    backgroundColor: '#f9f9f9',
    justifyContent: 'center',
  },
  dateButtonText: {
    fontSize: 14,
    color: '#000',
  },
  dateButtonPlaceholder: {
    color: '#999',
  },
  webDateInputWrapper: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: '#f9f9f9',
  },
  webDateInput: {
    width: '100%',
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 14,
    borderWidth: 0,
    fontFamily: 'System',
  },
  registerButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 14,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
    minHeight: 50,
  },
  registerButtonDisabled: {
    opacity: 0.6,
  },
  registerButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 8,
  },
  loginText: {
    fontSize: 14,
    color: '#666',
  },
  loginLink: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
});
