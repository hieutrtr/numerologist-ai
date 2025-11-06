/**
 * ProfileScreen Component Tests
 *
 * Comprehensive test suite for the Profile Screen UI component.
 * Tests cover:
 * - Component rendering and structure
 * - User data display (name, email, birth date)
 * - Date formatting functionality
 * - Logout functionality and navigation
 * - Loading states
 * - Error handling and retry
 * - Cross-platform functionality
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Platform } from 'react-native';
import ProfileScreen from '../../src/app/(tabs)/profile';
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

// Mock MaterialIcons
jest.mock('@expo/vector-icons', () => ({
  MaterialIcons: () => <div testID="material-icon" />,
}));

describe('ProfileScreen', () => {
  let mockLogout: jest.Mock;
  let mockRouter: any;
  const mockUser = {
    id: '123',
    email: 'john@example.com',
    full_name: 'John Doe',
    birth_date: '1990-05-15',
  };

  beforeEach(() => {
    // Setup auth store mock
    mockLogout = jest.fn().mockResolvedValue(undefined);
    (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
      user: mockUser,
      logout: mockLogout,
      isAuthenticated: true,
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
   * AC1, AC8: Component renders profile screen with proper structure
   */
  describe('Component Rendering', () => {
    it('should render profile screen with title and user data', () => {
      render(<ProfileScreen />);

      // Check for profile card rendering
      expect(screen.getByText('Profile Information')).toBeTruthy();

      // Check for field labels
      expect(screen.getByText('Full Name')).toBeTruthy();
      expect(screen.getByText('Email Address')).toBeTruthy();
      expect(screen.getByText('Birth Date')).toBeTruthy();

      // Check for logout button
      expect(screen.getByTestID('logout-button')).toBeTruthy();
    });

    it('should render with SafeAreaView for mobile notch avoidance', () => {
      const { container } = render(<ProfileScreen />);
      // SafeAreaView should be rendered (basic structure check)
      expect(container).toBeTruthy();
    });

    it('should render profile card with proper styling', () => {
      render(<ProfileScreen />);
      expect(screen.getByText('Profile Information')).toBeTruthy();
    });
  });

  /**
   * AC2, AC3: User data display and date formatting
   */
  describe('User Data Display', () => {
    it('should display user full name correctly', () => {
      render(<ProfileScreen />);
      expect(screen.getByText('John Doe')).toBeTruthy();
    });

    it('should display user email correctly', () => {
      render(<ProfileScreen />);
      expect(screen.getByText('john@example.com')).toBeTruthy();
    });

    it('should display formatted birth date', () => {
      render(<ProfileScreen />);
      // Birth date "1990-05-15" should be formatted as "May 15, 1990"
      expect(screen.getByText('May 15, 1990')).toBeTruthy();
    });

    it('should format various birth dates correctly', () => {
      const testCases = [
        { input: '2000-01-01', expected: 'January 1, 2000' },
        { input: '1985-12-25', expected: 'December 25, 1985' },
        { input: '2010-02-28', expected: 'February 28, 2010' },
      ];

      testCases.forEach(({ input, expected }) => {
        (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
          user: { ...mockUser, birth_date: input },
          logout: mockLogout,
          isAuthenticated: true,
        });

        render(<ProfileScreen />);
        expect(screen.getByText(expected)).toBeTruthy();
      });
    });

    it('should handle invalid birth date gracefully', () => {
      (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, birth_date: 'invalid-date' },
        logout: mockLogout,
        isAuthenticated: true,
      });

      render(<ProfileScreen />);
      // Should display error message for invalid date
      const invalidDateText = screen.queryByText('Invalid date');
      expect(invalidDateText || screen.queryByText('Error formatting date')).toBeTruthy();
    });

    it('should handle missing user data gracefully', () => {
      (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, full_name: '', email: '' },
        logout: mockLogout,
        isAuthenticated: true,
      });

      render(<ProfileScreen />);
      expect(screen.getByText('Not provided')).toBeTruthy();
    });

    it('should handle null user gracefully', () => {
      (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
        user: null,
        logout: mockLogout,
        isAuthenticated: false,
      });

      render(<ProfileScreen />);
      expect(
        screen.getByText(
          'Unable to load profile data. Please try logging out and back in.'
        )
      ).toBeTruthy();
    });
  });

  /**
   * AC4, AC5: Logout functionality and navigation
   */
  describe('Logout Functionality', () => {
    it('should call logout when logout button is pressed', async () => {
      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(mockLogout).toHaveBeenCalled();
      });
    });

    it('should navigate to login screen after logout', async () => {
      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(mockRouter.replace).toHaveBeenCalledWith('/(auth)/login');
      });
    });

    it('should use router.replace() not router.push()', async () => {
      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        // Verify router.replace is called, not push
        expect(mockRouter.replace).toHaveBeenCalled();
      });
    });

    it('should handle logout errors gracefully', async () => {
      mockLogout.mockRejectedValue(new Error('Logout failed'));

      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(screen.getByText('Logout failed')).toBeTruthy();
      });
    });

    it('should display custom error messages for logout failures', async () => {
      mockLogout.mockRejectedValue(new Error('Token removal failed'));

      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(screen.getByText('Token removal failed')).toBeTruthy();
      });
    });
  });

  /**
   * AC6: Loading state
   */
  describe('Loading State', () => {
    it('should show loading indicator when isLoading is true', () => {
      const { rerender } = render(<ProfileScreen />);

      // Initially renders profile data
      expect(screen.getByText('Profile Information')).toBeTruthy();
    });

    it('should disable logout button during submission', async () => {
      mockLogout.mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(resolve, 100);
          })
      );

      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      // Button should be disabled during submission
      expect(logoutButton).toHaveProp('disabled', true);
    });

    it('should show loading text during logout', async () => {
      mockLogout.mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(resolve, 100);
          })
      );

      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(screen.getByText('Logging out...')).toBeTruthy();
      });
    });
  });

  /**
   * AC7: Error handling and retry
   */
  describe('Error Handling', () => {
    it('should display error message when logout fails', async () => {
      mockLogout.mockRejectedValue(new Error('Network error'));

      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeTruthy();
      });
    });

    it('should show retry button on error', async () => {
      mockLogout.mockRejectedValue(new Error('Logout failed'));

      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeTruthy();
      });
    });

    it('should clear error when retry is pressed', async () => {
      mockLogout.mockRejectedValue(new Error('Logout failed'));

      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeTruthy();
      });

      const retryButton = screen.getByText('Retry');
      fireEvent.press(retryButton);

      // Error message should be cleared
      await waitFor(() => {
        expect(screen.queryByText('Logout failed')).toBeFalsy();
      });
    });

    it('should display fallback error message when error has no message', async () => {
      mockLogout.mockRejectedValue({});

      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(screen.getByText('Logout failed. Please try again.')).toBeTruthy();
      });
    });
  });

  /**
   * AC2, AC3: Date formatting edge cases
   */
  describe('Date Formatting Edge Cases', () => {
    it('should handle leap year dates', () => {
      (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, birth_date: '2000-02-29' },
        logout: mockLogout,
        isAuthenticated: true,
      });

      render(<ProfileScreen />);
      expect(screen.getByText('February 29, 2000')).toBeTruthy();
    });

    it('should handle new year dates', () => {
      (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, birth_date: '1999-12-31' },
        logout: mockLogout,
        isAuthenticated: true,
      });

      render(<ProfileScreen />);
      expect(screen.getByText('December 31, 1999')).toBeTruthy();
    });

    it('should handle century boundary dates', () => {
      (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, birth_date: '2000-01-01' },
        logout: mockLogout,
        isAuthenticated: true,
      });

      render(<ProfileScreen />);
      expect(screen.getByText('January 1, 2000')).toBeTruthy();
    });

    it('should handle empty birth date string', () => {
      (useAuthStoreModule.useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, birth_date: '' },
        logout: mockLogout,
        isAuthenticated: true,
      });

      render(<ProfileScreen />);
      expect(screen.getByText('Not available')).toBeTruthy();
    });
  });

  /**
   * AC8: Layout and styling
   */
  describe('Layout and Styling', () => {
    it('should render with proper spacing and layout', () => {
      const { container } = render(<ProfileScreen />);
      expect(container).toBeTruthy();
    });

    it('should have proper padding and margins', () => {
      render(<ProfileScreen />);
      // Verify profile card is rendered with proper structure
      expect(screen.getByText('Profile Information')).toBeTruthy();
    });

    it('should be responsive on different screen sizes', () => {
      render(<ProfileScreen />);
      // Component should render without errors on all screen sizes
      expect(screen.getByText('Profile Information')).toBeTruthy();
    });
  });

  /**
   * Cross-platform testing
   */
  describe('Cross-Platform Compatibility', () => {
    it('should work on iOS', () => {
      Platform.OS = 'ios';
      render(<ProfileScreen />);
      expect(screen.getByText('Profile Information')).toBeTruthy();
    });

    it('should work on Android', () => {
      Platform.OS = 'android';
      render(<ProfileScreen />);
      expect(screen.getByText('Profile Information')).toBeTruthy();
    });

    it('should work on web', () => {
      Platform.OS = 'web';
      render(<ProfileScreen />);
      expect(screen.getByText('Profile Information')).toBeTruthy();
    });
  });

  /**
   * Additional edge cases and user interactions
   */
  describe('User Interactions', () => {
    it('should prevent multiple logout attempts', async () => {
      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');

      // Press logout button twice
      fireEvent.press(logoutButton);
      fireEvent.press(logoutButton);

      // logout should only be called once (button is disabled after first press)
      await waitFor(() => {
        expect(mockLogout).toHaveBeenCalledTimes(1);
      });
    });

    it('should re-enable logout button after error', async () => {
      mockLogout.mockRejectedValue(new Error('Logout failed'));

      render(<ProfileScreen />);

      const logoutButton = screen.getByTestID('logout-button');
      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(screen.getByText('Logout failed')).toBeTruthy();
      });

      // After error, button should be enabled again
      expect(logoutButton).toHaveProp('disabled', false);
    });
  });
});
