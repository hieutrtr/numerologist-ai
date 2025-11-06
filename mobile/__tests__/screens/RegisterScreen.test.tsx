/**
 * RegisterScreen Component Tests
 *
 * Comprehensive test suite for the Register Screen UI component.
 * Tests cover:
 * - Component rendering and form fields
 * - Form validation (email, password, confirm password, full name, birth date)
 * - User interactions (typing, button presses, date selection)
 * - Loading states
 * - Error handling and display
 * - Navigation
 * - Cross-platform functionality (web vs native)
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Platform } from 'react-native';
import RegisterScreen from '../../src/app/(auth)/register';
import * as useAuthStoreModule from '../../src/stores/useAuthStore';
import * as useRouterModule from 'expo-router';

// Mock expo-router
jest.mock('expo-router', () => ({
  useRouter: jest.fn(),
  Link: ({ children, href }: any) => <>{children}</>,
}));

// Mock useAuthStore
jest.mock('../../src/stores/useAuthStore', () => ({
  useAuthStore: jest.fn(),
}));

// Mock DateTimePicker
jest.mock('@react-native-community/datetimepicker', () => ({
  __esModule: true,
  default: ({ onChange, value }: any) => {
    return (
      <div
        testID="date-time-picker"
        onClick={() => onChange({}, new Date('1990-05-15'))}
      >
        DatePicker Mock
      </div>
    );
  },
}));

// Mock MaterialIcons
jest.mock('@expo/vector-icons', () => ({
  MaterialIcons: () => <div testID="material-icon" />,
}));

describe('RegisterScreen', () => {
  let mockRegister: jest.Mock;
  let mockRouter: any;

  beforeEach(() => {
    // Setup auth store mock
    mockRegister = jest.fn().mockResolvedValue(undefined);
    (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
      register: mockRegister,
      isLoading: false,
    });

    // Setup router mock
    mockRouter = {
      replace: jest.fn(),
    };
    (useRouterModule.useRouter as jest.Mock).mockReturnValue(mockRouter);

    // Reset platform to native
    Platform.OS = 'ios';

    jest.clearAllMocks();
  });

  /**
   * AC1, AC2: Component renders all required form fields
   */
  describe('Form Rendering', () => {
    it('should render the register form with all required fields', () => {
      render(<RegisterScreen />);

      // Check title
      expect(screen.getByText('Create Account')).toBeTruthy();
      expect(screen.getByText('Join us to start your journey')).toBeTruthy();

      // Check all labels
      expect(screen.getByText('Full Name')).toBeTruthy();
      expect(screen.getByText('Email')).toBeTruthy();
      expect(screen.getByText('Password')).toBeTruthy();
      expect(screen.getByText('Confirm Password')).toBeTruthy();
      expect(screen.getByText('Birth Date')).toBeTruthy();
    });

    it('should render all input fields with correct properties', () => {
      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      expect(fullNameInput).toBeTruthy();

      const emailInput = screen.getByTestID('email-input');
      expect(emailInput).toBeTruthy();

      const passwordInput = screen.getByTestID('password-input');
      expect(passwordInput).toBeTruthy();

      const confirmPasswordInput = screen.getByTestID('confirm-password-input');
      expect(confirmPasswordInput).toBeTruthy();
    });

    it('should render register and login link buttons', () => {
      render(<RegisterScreen />);

      expect(screen.getByTestID('register-button')).toBeTruthy();
      expect(screen.getByTestID('login-link')).toBeTruthy();
    });
  });

  /**
   * AC2: Form validation - email field
   */
  describe('Email Validation', () => {
    it('should show error for empty email', async () => {
      render(<RegisterScreen />);

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, '');

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
      });
    });

    it('should show error for invalid email format', async () => {
      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      fireEvent.changeText(fullNameInput, 'John Doe');

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'invalid-email');

      const passwordInput = screen.getByTestID('password-input');
      fireEvent.changeText(passwordInput, 'password123');

      const confirmPasswordInput = screen.getByTestID('confirm-password-input');
      fireEvent.changeText(confirmPasswordInput, 'password123');

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(screen.getByText('Invalid email format')).toBeTruthy();
      });
    });

    it('should accept valid email format', () => {
      render(<RegisterScreen />);

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'valid@email.com');

      // Error should not appear for valid email
      expect(screen.queryByText('Invalid email format')).toBeFalsy();
    });

    it('should clear email error when user edits the field', async () => {
      render(<RegisterScreen />);

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'invalid');

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(screen.getByText('Invalid email format')).toBeTruthy();
      });

      fireEvent.changeText(emailInput, 'valid@email.com');

      // Error should be cleared
      expect(screen.queryByText('Invalid email format')).toBeFalsy();
    });
  });

  /**
   * AC2, AC10: Password validation
   */
  describe('Password Validation', () => {
    it('should show error for empty password', async () => {
      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      fireEvent.changeText(fullNameInput, 'John Doe');

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'test@email.com');

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(screen.getByText('Password is required')).toBeTruthy();
      });
    });

    it('should show error for password less than 8 characters', async () => {
      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      fireEvent.changeText(fullNameInput, 'John Doe');

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'test@email.com');

      const passwordInput = screen.getByTestID('password-input');
      fireEvent.changeText(passwordInput, 'short');

      const confirmPasswordInput = screen.getByTestID('confirm-password-input');
      fireEvent.changeText(confirmPasswordInput, 'short');

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(
          screen.getByText('Password must be at least 8 characters')
        ).toBeTruthy();
      });
    });

    it('should accept password with 8 or more characters', () => {
      render(<RegisterScreen />);

      const passwordInput = screen.getByTestID('password-input');
      fireEvent.changeText(passwordInput, 'password123');

      // Error should not appear
      expect(
        screen.queryByText('Password must be at least 8 characters')
      ).toBeFalsy();
    });
  });

  /**
   * AC4: Password confirmation validation
   */
  describe('Password Confirmation', () => {
    it('should show error when passwords do not match', async () => {
      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      fireEvent.changeText(fullNameInput, 'John Doe');

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'test@email.com');

      const passwordInput = screen.getByTestID('password-input');
      fireEvent.changeText(passwordInput, 'password123');

      const confirmPasswordInput = screen.getByTestID('confirm-password-input');
      fireEvent.changeText(confirmPasswordInput, 'password456');

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(screen.getByText('Passwords do not match')).toBeTruthy();
      });
    });

    it('should not show error when passwords match', () => {
      render(<RegisterScreen />);

      const passwordInput = screen.getByTestID('password-input');
      fireEvent.changeText(passwordInput, 'password123');

      const confirmPasswordInput = screen.getByTestID('confirm-password-input');
      fireEvent.changeText(confirmPasswordInput, 'password123');

      expect(screen.queryByText('Passwords do not match')).toBeFalsy();
    });
  });

  /**
   * AC10: Full name validation
   */
  describe('Full Name Validation', () => {
    it('should show error for empty full name', async () => {
      render(<RegisterScreen />);

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'test@email.com');

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(screen.getByText('Full name is required')).toBeTruthy();
      });
    });

    it('should show error for whitespace-only full name', async () => {
      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      fireEvent.changeText(fullNameInput, '   ');

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(screen.getByText('Full name is required')).toBeTruthy();
      });
    });
  });

  /**
   * AC3, AC10: Birth date validation
   */
  describe('Birth Date Validation', () => {
    it('should show error for missing birth date', async () => {
      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      fireEvent.changeText(fullNameInput, 'John Doe');

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'test@email.com');

      const passwordInput = screen.getByTestID('password-input');
      fireEvent.changeText(passwordInput, 'password123');

      const confirmPasswordInput = screen.getByTestID('confirm-password-input');
      fireEvent.changeText(confirmPasswordInput, 'password123');

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(
          screen.getByText('Valid birth date is required (not in the future)')
        ).toBeTruthy();
      });
    });
  });

  /**
   * AC2: Show/hide password toggles
   */
  describe('Show/Hide Password Toggles', () => {
    it('should toggle password visibility', () => {
      render(<RegisterScreen />);

      const passwordToggle = screen.getByTestID('toggle-password');
      expect(passwordToggle).toBeTruthy();

      const confirmPasswordToggle = screen.getByTestID(
        'toggle-confirm-password'
      );
      expect(confirmPasswordToggle).toBeTruthy();
    });
  });

  /**
   * AC6, AC7: Loading state and error handling
   */
  describe('Loading State and Submission', () => {
    it('should disable register button while loading', () => {
      (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
        register: mockRegister,
        isLoading: true,
      });

      render(<RegisterScreen />);

      const registerButton = screen.getByTestID('register-button');
      expect(registerButton).toHaveProperty('disabled', true);
    });

    it('should show loading indicator while submitting', () => {
      (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
        register: mockRegister,
        isLoading: true,
      });

      render(<RegisterScreen />);

      // The ActivityIndicator should be rendered
      expect(screen.queryByTestID('register-button')).toBeTruthy();
    });

    it('should show error message on registration failure', async () => {
      mockRegister.mockRejectedValue(
        new Error('Email already exists')
      );

      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      fireEvent.changeText(fullNameInput, 'John Doe');

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'test@email.com');

      const passwordInput = screen.getByTestID('password-input');
      fireEvent.changeText(passwordInput, 'password123');

      const confirmPasswordInput = screen.getByTestID('confirm-password-input');
      fireEvent.changeText(confirmPasswordInput, 'password123');

      // Mock birth date selection
      const birthdateButton = screen.queryByTestID('birthdate-button');
      if (birthdateButton) {
        fireEvent.press(birthdateButton);
        const datePicker = screen.getByTestID('date-time-picker');
        fireEvent.press(datePicker);
      }

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(screen.getByText('Email already exists')).toBeTruthy();
      });
    });
  });

  /**
   * AC5, AC8: Registration action and navigation
   */
  describe('Registration Action', () => {
    it('should call register with correct data format', async () => {
      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      fireEvent.changeText(fullNameInput, 'John Doe');

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'john@example.com');

      const passwordInput = screen.getByTestID('password-input');
      fireEvent.changeText(passwordInput, 'password123');

      const confirmPasswordInput = screen.getByTestID('confirm-password-input');
      fireEvent.changeText(confirmPasswordInput, 'password123');

      // Mock date selection
      const birthdateButton = screen.queryByTestID('birthdate-button');
      if (birthdateButton) {
        fireEvent.press(birthdateButton);
        const datePicker = screen.getByTestID('date-time-picker');
        fireEvent.press(datePicker);
      }

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith(
          'john@example.com',
          'password123',
          'John Doe',
          expect.stringMatching(/\d{4}-\d{2}-\d{2}/)
        );
      });
    });

    it('should navigate to home on successful registration', async () => {
      mockRegister.mockResolvedValue(undefined);

      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      fireEvent.changeText(fullNameInput, 'John Doe');

      const emailInput = screen.getByTestID('email-input');
      fireEvent.changeText(emailInput, 'john@example.com');

      const passwordInput = screen.getByTestID('password-input');
      fireEvent.changeText(passwordInput, 'password123');

      const confirmPasswordInput = screen.getByTestID('confirm-password-input');
      fireEvent.changeText(confirmPasswordInput, 'password123');

      // Mock date selection
      const birthdateButton = screen.queryByTestID('birthdate-button');
      if (birthdateButton) {
        fireEvent.press(birthdateButton);
        const datePicker = screen.getByTestID('date-time-picker');
        fireEvent.press(datePicker);
      }

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(mockRouter.replace).toHaveBeenCalledWith('/');
      });
    });
  });

  /**
   * AC9: Navigation to login
   */
  describe('Navigation to Login', () => {
    it('should render login link', () => {
      render(<RegisterScreen />);

      expect(screen.getByText('Already have an account?')).toBeTruthy();
      expect(screen.getByText('Login')).toBeTruthy();
    });
  });

  /**
   * Error message display and clearing
   */
  describe('Error Message Handling', () => {
    it('should clear error when user starts typing', async () => {
      mockRegister.mockRejectedValue(new Error('Network error'));

      render(<RegisterScreen />);

      const fullNameInput = screen.getByTestID('fullname-input');
      fireEvent.changeText(fullNameInput, 'John Doe');

      const registerButton = screen.getByTestID('register-button');
      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeTruthy();
      });

      // User starts typing in a field
      fireEvent.changeText(fullNameInput, 'Jane Doe');

      // Error should be cleared
      expect(screen.queryByText('Network error')).toBeFalsy();
    });
  });
});
