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
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Link } from 'expo-router';
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

  // Auth store
  const { register } = useAuthStore();

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

      // Navigation is handled automatically by root layout based on auth state
      // No need to manually navigate - the root layout will detect isAuthenticated=true
      // and redirect to home automatically
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
    <SafeAreaView className="flex-1 bg-dark">
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1"
      >
        <ScrollView
          contentContainerStyle={{ flexGrow: 1, justifyContent: 'center' }}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View className="px-lg py-xxl">
            {/* Header */}
            <View className="mb-xxxl items-center">
              <Text className="text-display font-bold text-text-primary mb-md">Create Account</Text>
              <Text className="text-body text-text-secondary font-normal">Join us to start your journey</Text>
            </View>

            {/* Error Message Display */}
            {error && (
              <View className="bg-error/20 border border-error rounded-lg p-md mb-lg">
                <Text className="text-error font-semibold text-small">{error}</Text>
              </View>
            )}

            {/* Form Fields */}
            <View className="mb-lg">
              {/* Full Name Input */}
              <View className="mb-md">
                <Text className="text-small font-semibold text-text-primary mb-xs">Full Name</Text>
                <TextInput
                  className={`border rounded-lg px-md py-md text-body font-normal text-text-primary ${
                    fieldErrors.fullName ? 'border-error bg-error/10' : 'border-border bg-light'
                  }`}
                  placeholder="John Doe"
                  placeholderTextColor="#6b7280"
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
                  <Text className="text-error text-tiny mt-xs font-medium">{fieldErrors.fullName}</Text>
                )}
              </View>

              {/* Email Input */}
              <View className="mb-md">
                <Text className="text-small font-semibold text-text-primary mb-xs">Email</Text>
                <TextInput
                  ref={emailInputRef}
                  className={`border rounded-lg px-md py-md text-body font-normal text-text-primary ${
                    fieldErrors.email ? 'border-error bg-error/10' : 'border-border bg-light'
                  }`}
                  placeholder="your@email.com"
                  placeholderTextColor="#6b7280"
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
                  <Text className="text-error text-tiny mt-xs font-medium">{fieldErrors.email}</Text>
                )}
              </View>

              {/* Password Input with Show/Hide Toggle */}
              <View className="mb-md">
                <Text className="text-small font-semibold text-text-primary mb-xs">Password</Text>
                <View className="flex-row items-center relative">
                  <TextInput
                    ref={passwordInputRef}
                    className={`flex-1 border rounded-lg px-md py-md text-body font-normal text-text-primary ${
                      fieldErrors.password ? 'border-error bg-error/10' : 'border-border bg-light'
                    }`}
                    placeholder="••••••••"
                    placeholderTextColor="#6b7280"
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
                    className="absolute right-md py-md px-sm"
                    onPress={() => setShowPassword(!showPassword)}
                    disabled={isSubmitting}
                    testID="toggle-password"
                  >
                    <MaterialIcons
                      name={showPassword ? 'visibility' : 'visibility-off'}
                      size={20}
                      color="#6b7280"
                    />
                  </TouchableOpacity>
                </View>
                {fieldErrors.password && (
                  <Text className="text-error text-tiny mt-xs font-medium">
                    {fieldErrors.password}
                  </Text>
                )}
              </View>

              {/* Confirm Password Input with Show/Hide Toggle */}
              <View className="mb-md">
                <Text className="text-small font-semibold text-text-primary mb-xs">Confirm Password</Text>
                <View className="flex-row items-center relative">
                  <TextInput
                    ref={confirmPasswordInputRef}
                    className={`flex-1 border rounded-lg px-md py-md text-body font-normal text-text-primary ${
                      fieldErrors.confirmPassword ? 'border-error bg-error/10' : 'border-border bg-light'
                    }`}
                    placeholder="••••••••"
                    placeholderTextColor="#6b7280"
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
                    className="absolute right-md py-md px-sm"
                    onPress={() =>
                      setShowConfirmPassword(!showConfirmPassword)
                    }
                    disabled={isSubmitting}
                    testID="toggle-confirm-password"
                  >
                    <MaterialIcons
                      name={showConfirmPassword ? 'visibility' : 'visibility-off'}
                      size={20}
                      color="#6b7280"
                    />
                  </TouchableOpacity>
                </View>
                {fieldErrors.confirmPassword && (
                  <Text className="text-error text-tiny mt-xs font-medium">
                    {fieldErrors.confirmPassword}
                  </Text>
                )}
              </View>

              {/* Birth Date Input */}
              <View className="mb-md">
                <Text className="text-small font-semibold text-text-primary mb-xs">Birth Date</Text>
                {Platform.OS === 'web' ? (
                  // Web: HTML date input
                  <View className="border border-border rounded-lg overflow-hidden bg-light">
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
                      style={{
                        width: '100%',
                        paddingLeft: 16,
                        paddingRight: 16,
                        paddingTop: 16,
                        paddingBottom: 16,
                        fontSize: 16,
                        borderWidth: 0,
                        fontFamily: 'System',
                      }}
                      disabled={isSubmitting}
                    />
                  </View>
                ) : (
                  // Mobile: Touchable button with date picker modal
                  <>
                    <TouchableOpacity
                      className={`border rounded-lg px-md py-md justify-center ${
                        fieldErrors.birthDate ? 'border-error bg-error/10' : 'border-border bg-light'
                      }`}
                      onPress={() => setShowDatePicker(true)}
                      disabled={isSubmitting}
                      testID="birthdate-button"
                    >
                      <Text
                        className={`text-body ${
                          !birthDate ? 'text-text-muted' : 'text-text-primary'
                        }`}
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
                  <Text className="text-error text-tiny mt-xs font-medium">
                    {fieldErrors.birthDate}
                  </Text>
                )}
              </View>
            </View>

            {/* Register Button */}
            <TouchableOpacity
              className={`bg-primary rounded-lg py-sm px-md items-center justify-center mb-lg min-h-[50px] ${
                isRegisterDisabled ? 'opacity-60' : ''
              }`}
              onPress={handleRegister}
              disabled={isRegisterDisabled}
              testID="register-button"
            >
              {isSubmitting ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <Text className="text-body font-semibold text-white">Register</Text>
              )}
            </TouchableOpacity>

            {/* Login Link */}
            <View className="flex-row justify-center items-center py-sm">
              <Text className="text-small text-text-secondary">Already have an account? </Text>
              <Link href="/(auth)/login" asChild>
                <TouchableOpacity testID="login-link">
                  <Text className="text-small text-primary font-semibold">Login</Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
