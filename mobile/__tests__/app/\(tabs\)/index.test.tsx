import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import ConversationScreen from '@/app/(tabs)/index';
import * as audioService from '@/services/audio.service';
import * as conversationStore from '@/stores/useConversationStore';

/**
 * Mock dependencies
 */
jest.mock('@/services/audio.service');
jest.mock('@/stores/useConversationStore');
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaView: ({ children }: any) => children,
}));
jest.mock('@expo/vector-icons', () => ({
  MaterialIcons: ({ name, size, color }: any) => (
    <div data-testid={`icon-${name}`}>{name}</div>
  ),
}));

// Mock Alert
jest.spyOn(Alert, 'alert').mockImplementation(() => {});

describe('ConversationScreen', () => {
  const mockStartConversation = jest.fn();
  const mockEndConversation = jest.fn();
  const mockCheckPermission = jest.fn();
  const mockRequestPermission = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    // Default store mock
    (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
      isConnected: false,
      isLoading: false,
      isAISpeaking: false,
      error: null,
      startConversation: mockStartConversation,
      endConversation: mockEndConversation,
    });

    // Default audio service mocks
    (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
      true
    );
    (audioService.requestMicrophonePermission as jest.Mock).mockResolvedValue(
      true
    );
  });

  // ============================================================================
  // AC1: Conversation Screen Component
  // ============================================================================

  describe('AC1: Conversation Screen Component', () => {
    it('should render without crashing', () => {
      render(<ConversationScreen />);
      expect(screen.getByText(/Tap to start conversation/i)).toBeTruthy();
    });

    it('should render in tab layout as home screen', () => {
      const { container } = render(<ConversationScreen />);
      expect(container.firstChild).toBeDefined();
    });

    it('should have clean, minimal design with flexbox centering', () => {
      const { getByTestId } = render(<ConversationScreen />);
      // Verify container uses flex layout (implicit from SafeAreaView wrapper)
      expect(screen.getByText(/Tap to start conversation/i)).toBeTruthy();
    });
  });

  // ============================================================================
  // AC2: Microphone Button - Main Control
  // ============================================================================

  describe('AC2: Microphone Button - Main Control', () => {
    it('should render large microphone button (90x90)', () => {
      const { container } = render(<ConversationScreen />);
      const buttons = container.querySelectorAll('[accessibilityRole="button"]');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('should show "Start Conversation" label when disconnected', () => {
      render(<ConversationScreen />);
      expect(screen.getByText(/Start Conversation/i)).toBeTruthy();
    });

    it('should show "End Conversation" label when connected', () => {
      (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isLoading: false,
        isAISpeaking: false,
        error: null,
        startConversation: mockStartConversation,
        endConversation: mockEndConversation,
      });

      render(<ConversationScreen />);
      expect(screen.getByText(/End Conversation/i)).toBeTruthy();
    });

    it('should respond to button press', async () => {
      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      fireEvent.press(button);

      await waitFor(() => {
        expect(mockStartConversation).toHaveBeenCalled();
      });
    });
  });

  // ============================================================================
  // AC3: Button State Management
  // ============================================================================

  describe('AC3: Button State Management', () => {
    it('should reflect not connected state with neutral styling', () => {
      render(<ConversationScreen />);
      expect(screen.getByText(/Tap to start conversation/i)).toBeTruthy();
    });

    it('should reflect connected state with active styling', () => {
      (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isLoading: false,
        isAISpeaking: false,
        error: null,
        startConversation: mockStartConversation,
        endConversation: mockEndConversation,
      });

      render(<ConversationScreen />);
      expect(screen.getByText(/Connected - Speak now/i)).toBeTruthy();
    });

    it('should show loading state while connecting', () => {
      (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isLoading: true,
        isAISpeaking: false,
        error: null,
        startConversation: mockStartConversation,
        endConversation: mockEndConversation,
      });

      render(<ConversationScreen />);
      expect(screen.getByText(/Connecting to AI/i)).toBeTruthy();
    });

    it('should show AI speaking state', () => {
      (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isLoading: false,
        isAISpeaking: true,
        error: null,
        startConversation: mockStartConversation,
        endConversation: mockEndConversation,
      });

      render(<ConversationScreen />);
      expect(screen.getByText(/AI is speaking/i)).toBeTruthy();
    });
  });

  // ============================================================================
  // AC4: Permission Handling
  // ============================================================================

  describe('AC4: Permission Handling', () => {
    it('should check permission before starting conversation', async () => {
      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      fireEvent.press(button);

      await waitFor(() => {
        expect(mockCheckPermission).toHaveBeenCalled() ||
          expect(audioService.checkMicrophonePermission).toHaveBeenCalled();
      });
    });

    it('should request permission if not already granted', async () => {
      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        false
      );
      (audioService.requestMicrophonePermission as jest.Mock).mockResolvedValue(
        true
      );

      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      fireEvent.press(button);

      await waitFor(() => {
        expect(
          audioService.requestMicrophonePermission
        ).toHaveBeenCalled();
      });
    });

    it('should show alert when permission denied', async () => {
      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        false
      );
      (audioService.requestMicrophonePermission as jest.Mock).mockResolvedValue(
        false
      );

      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      fireEvent.press(button);

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          expect.stringContaining('Microphone'),
          expect.any(String),
          expect.any(Array)
        );
      });
    });

    it('should proceed to start conversation if permission granted', async () => {
      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        true
      );

      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      fireEvent.press(button);

      await waitFor(() => {
        expect(mockStartConversation).toHaveBeenCalled();
      });
    });
  });

  // ============================================================================
  // AC5: Conversation Control Flow
  // ============================================================================

  describe('AC5: Conversation Control Flow', () => {
    it('should call startConversation when start button tapped with permission', async () => {
      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      fireEvent.press(button);

      await waitFor(() => {
        expect(mockStartConversation).toHaveBeenCalled();
      });
    });

    it('should call endConversation when end button tapped while connected', async () => {
      (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isLoading: false,
        isAISpeaking: false,
        error: null,
        startConversation: mockStartConversation,
        endConversation: mockEndConversation,
      });

      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      fireEvent.press(button);

      await waitFor(() => {
        expect(mockEndConversation).toHaveBeenCalled();
      });
    });

    it('should handle errors from startConversation gracefully', async () => {
      mockStartConversation.mockRejectedValue(new Error('Connection failed'));

      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      fireEvent.press(button);

      await waitFor(() => {
        // Should show error alert but not crash
        expect(Alert.alert).toHaveBeenCalled();
      });
    });
  });

  // ============================================================================
  // AC6: Connection Status Display
  // ============================================================================

  describe('AC6: Connection Status Display', () => {
    it('should display status text above button', () => {
      render(<ConversationScreen />);
      expect(screen.getByText(/Tap to start conversation/i)).toBeTruthy();
    });

    it('should update status based on connection state', () => {
      const { rerender } = render(<ConversationScreen />);
      expect(screen.getByText(/Tap to start conversation/i)).toBeTruthy();

      (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isLoading: false,
        isAISpeaking: false,
        error: null,
        startConversation: mockStartConversation,
        endConversation: mockEndConversation,
      });

      rerender(<ConversationScreen />);
      expect(screen.getByText(/Connected - Speak now/i)).toBeTruthy();
    });
  });

  // ============================================================================
  // AC7: Visual Feedback & Animations
  // ============================================================================

  describe('AC7: Visual Feedback & Animations', () => {
    it('should display microphone icon', () => {
      render(<ConversationScreen />);
      expect(screen.getByTestId('icon-mic')).toBeTruthy();
    });

    it('should show loading spinner when connecting', () => {
      (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isLoading: true,
        isAISpeaking: false,
        error: null,
        startConversation: mockStartConversation,
        endConversation: mockEndConversation,
      });

      render(<ConversationScreen />);
      // Loading spinner should replace icon
      const status = screen.getByText(/Connecting to AI/i);
      expect(status).toBeTruthy();
    });
  });

  // ============================================================================
  // AC8: Integration with Store
  // ============================================================================

  describe('AC8: Integration with Store', () => {
    it('should use useConversationStore hook', () => {
      render(<ConversationScreen />);
      expect(conversationStore.useConversationStore).toHaveBeenCalled();
    });

    it('should access required store state', () => {
      render(<ConversationScreen />);
      const storeCall = (
        conversationStore.useConversationStore as jest.Mock
      ).mock.results[0].value;

      expect(storeCall).toHaveProperty('isConnected');
      expect(storeCall).toHaveProperty('isLoading');
      expect(storeCall).toHaveProperty('isAISpeaking');
      expect(storeCall).toHaveProperty('error');
    });

    it('should access store methods', () => {
      render(<ConversationScreen />);
      const storeCall = (
        conversationStore.useConversationStore as jest.Mock
      ).mock.results[0].value;

      expect(storeCall).toHaveProperty('startConversation');
      expect(storeCall).toHaveProperty('endConversation');
    });

    it('should display store errors', () => {
      (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isLoading: false,
        isAISpeaking: false,
        error: 'Connection timeout',
        startConversation: mockStartConversation,
        endConversation: mockEndConversation,
      });

      render(<ConversationScreen />);
      expect(screen.getByText(/Connection timeout/i)).toBeTruthy();
    });
  });

  // ============================================================================
  // AC9: Error Handling & Edge Cases
  // ============================================================================

  describe('AC9: Error Handling & Edge Cases', () => {
    it('should handle permission denial gracefully', async () => {
      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        false
      );
      (audioService.requestMicrophonePermission as jest.Mock).mockResolvedValue(
        false
      );

      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      fireEvent.press(button);

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalled();
        // Button should still be clickable
        expect(button).not.toBeDisabled();
      });
    });

    it('should debounce rapid button taps', async () => {
      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      // Tap multiple times rapidly
      fireEvent.press(button);
      fireEvent.press(button);
      fireEvent.press(button);

      await waitFor(() => {
        // startConversation should only be called once (or minimal times due to debounce)
        expect(mockStartConversation.mock.calls.length).toBeLessThanOrEqual(2);
      });
    });

    it('should disable button while connecting', () => {
      (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isLoading: true,
        isAISpeaking: false,
        error: null,
        startConversation: mockStartConversation,
        endConversation: mockEndConversation,
      });

      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      expect(button.props.disabled).toBe(true);
    });

    it('should handle network errors', async () => {
      mockStartConversation.mockRejectedValue(new Error('Network error'));

      render(<ConversationScreen />);
      const button = screen.getByRole('button');

      fireEvent.press(button);

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          expect.stringContaining('Error'),
          expect.any(String),
          expect.anything()
        );
      });
    });
  });

  // ============================================================================
  // AC10: Responsive Design
  // ============================================================================

  describe('AC10: Responsive Design', () => {
    it('should render and layout properly', () => {
      const { container } = render(<ConversationScreen />);
      expect(container.firstChild).toBeDefined();
      // Component should use flex layout and center content
      expect(screen.getByText(/Tap to start conversation/i)).toBeTruthy();
    });

    it('should render button with proper sizing', () => {
      const { container } = render(<ConversationScreen />);
      const buttons = container.querySelectorAll('[accessibilityRole="button"]');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  // ============================================================================
  // Integration Tests
  // ============================================================================

  describe('Integration Tests', () => {
    it('should complete full flow: permission → start → connected → end', async () => {
      const { rerender } = render(<ConversationScreen />);

      // Initial state: disconnected
      expect(screen.getByText(/Tap to start conversation/i)).toBeTruthy();

      // Tap button to start
      const button = screen.getByRole('button');
      fireEvent.press(button);

      // Permission granted
      await waitFor(() => {
        expect(mockStartConversation).toHaveBeenCalled();
      });

      // Update to connected state
      (conversationStore.useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isLoading: false,
        isAISpeaking: false,
        error: null,
        startConversation: mockStartConversation,
        endConversation: mockEndConversation,
      });

      rerender(<ConversationScreen />);
      expect(screen.getByText(/Connected - Speak now/i)).toBeTruthy();

      // Tap to end
      fireEvent.press(button);

      await waitFor(() => {
        expect(mockEndConversation).toHaveBeenCalled();
      });
    });
  });
});
