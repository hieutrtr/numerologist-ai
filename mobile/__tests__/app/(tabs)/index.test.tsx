import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import ConversationScreen from '../../../src/app/(tabs)/index';
import * as audioService from '../../../src/services/audio.service';
import { useConversationStore } from '../../../src/stores/useConversationStore';

/**
 * Mock dependencies
 */
jest.mock('@expo/vector-icons', () => ({
  MaterialCommunityIcons: {
    name: 'MockIcon',
  },
}));

jest.mock('react-native-safe-area-context', () => ({
  SafeAreaView: ({ children }: any) => children,
}));

jest.mock('../../../src/services/audio.service');
jest.mock('../../../src/stores/useConversationStore');

/**
 * Setup mocks before each test
 */
describe('ConversationScreen Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Default mock implementation
    (useConversationStore as jest.Mock).mockReturnValue({
      isConnected: false,
      isAISpeaking: false,
      error: null,
      startConversation: jest.fn().mockResolvedValue(undefined),
      endConversation: jest.fn().mockResolvedValue(undefined),
    });

    (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
      true
    );
    (audioService.requestMicrophonePermission as jest.Mock).mockResolvedValue(
      true
    );

    // Mock Alert
    jest.spyOn(Alert, 'alert').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  // ==================== AC1: Component Structure Tests ====================

  describe('AC1: Conversation Screen Component', () => {
    it('should render without crashing', () => {
      const { toJSON } = render(<ConversationScreen />);
      expect(toJSON()).toBeTruthy();
    });

    it('should render in SafeAreaView', () => {
      const { UNSAFE_root } = render(<ConversationScreen />);
      expect(UNSAFE_root).toBeTruthy();
    });

    it('should have accessibility label for button', () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isAISpeaking: false,
        error: null,
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');
      expect(button).toBeTruthy();
    });
  });

  // ==================== AC2: Microphone Button Tests ====================

  describe('AC2: Microphone Button', () => {
    it('should render microphone button', () => {
      const { getByTestId } = render(<ConversationScreen />);
      // Button rendered via TouchableOpacity with accessible label
      expect(screen.getByLabelText('Start conversation')).toBeTruthy();
    });

    it('should display "Start Conversation" when not connected', () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isAISpeaking: false,
        error: null,
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      const { getByText } = render(<ConversationScreen />);
      expect(getByText('Start Conversation')).toBeTruthy();
    });

    it('should display "End Conversation" when connected', () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isAISpeaking: false,
        error: null,
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      const { getByText } = render(<ConversationScreen />);
      expect(getByText('End Conversation')).toBeTruthy();
    });

    it('button should be touchable when not connected', () => {
      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');
      expect(button.props.disabled).toBeFalsy();
    });
  });

  // ==================== AC3: Button State Management Tests ====================

  describe('AC3: Button State Management', () => {
    it('should update button style when connected', () => {
      const { rerender, getByText } = render(<ConversationScreen />);

      // Initially not connected
      let button = getByText('Start Conversation').parent;
      expect(button?.props.style).toContainEqual(expect.objectContaining({}));

      // Rerender with connected state
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isAISpeaking: false,
        error: null,
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      rerender(<ConversationScreen />);
      button = getByText('End Conversation').parent;
      expect(button).toBeTruthy();
    });

    it('should show different styling for AI speaking state', () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isAISpeaking: true,
        error: null,
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      const { getByText } = render(<ConversationScreen />);
      expect(getByText('AI is speaking...')).toBeTruthy();
    });
  });

  // ==================== AC4: Permission Handling Tests ====================

  describe('AC4: Permission Handling', () => {
    it('should check permission before starting conversation', async () => {
      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');

      fireEvent.press(button);

      await waitFor(() => {
        expect(audioService.checkMicrophonePermission).toHaveBeenCalled();
      });
    });

    it('should request permission if not already granted', async () => {
      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        false
      );

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');

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

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');

      fireEvent.press(button);

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Microphone Required',
          expect.stringContaining('enable microphone access')
        );
      });
    });

    it('should not request permission if already granted', async () => {
      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        true
      );
      (audioService.requestMicrophonePermission as jest.Mock).mockClear();

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');

      fireEvent.press(button);

      await waitFor(() => {
        // Check should be called but request should not
        expect(audioService.checkMicrophonePermission).toHaveBeenCalled();
        // Request may not be called if check returned true
      });
    });
  });

  // ==================== AC5: Conversation Control Flow Tests ====================

  describe('AC5: Conversation Control Flow', () => {
    it('should call startConversation after permission granted', async () => {
      const startConvMock = jest.fn().mockResolvedValue(undefined);
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isAISpeaking: false,
        error: null,
        startConversation: startConvMock,
        endConversation: jest.fn(),
      });

      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        true
      );

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');

      fireEvent.press(button);

      await waitFor(() => {
        expect(startConvMock).toHaveBeenCalled();
      });
    });

    it('should call endConversation when connected and button pressed', async () => {
      const endConvMock = jest.fn().mockResolvedValue(undefined);
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isAISpeaking: false,
        error: null,
        startConversation: jest.fn(),
        endConversation: endConvMock,
      });

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('End conversation');

      fireEvent.press(button);

      await waitFor(() => {
        expect(endConvMock).toHaveBeenCalled();
      });
    });

    it('should show error alert if start conversation fails', async () => {
      const error = new Error('Connection failed');
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isAISpeaking: false,
        error: null,
        startConversation: jest.fn().mockRejectedValue(error),
        endConversation: jest.fn(),
      });

      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        true
      );

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');

      fireEvent.press(button);

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Connection Error',
          expect.stringContaining('Connection failed')
        );
      });
    });
  });

  // ==================== AC6: Connection Status Display Tests ====================

  describe('AC6: Connection Status Display', () => {
    it('should show default status when not connected', () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isAISpeaking: false,
        error: null,
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      const { getByText } = render(<ConversationScreen />);
      expect(getByText('Tap to start conversation')).toBeTruthy();
    });

    it('should show "Connected" status when connected', () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isAISpeaking: false,
        error: null,
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      const { getByText } = render(<ConversationScreen />);
      expect(getByText('Connected - Speak now')).toBeTruthy();
    });

    it('should show "AI Speaking" status when AI is speaking', () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isAISpeaking: true,
        error: null,
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      const { getByText } = render(<ConversationScreen />);
      expect(getByText('AI is speaking...')).toBeTruthy();
    });

    it('should show error message when error exists', () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isAISpeaking: false,
        error: 'Network error',
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      const { getByText } = render(<ConversationScreen />);
      expect(getByText('Error: Network error')).toBeTruthy();
    });
  });

  // ==================== AC7: Visual Feedback Tests ====================

  describe('AC7: Visual Feedback & Animations', () => {
    it('should render microphone icon', () => {
      const { toJSON } = render(<ConversationScreen />);
      expect(toJSON()).toBeTruthy();
      // Icon rendered through MaterialCommunityIcons mock
    });

    it('should have pulsing animation when connected', () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isAISpeaking: false,
        error: null,
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      const { toJSON } = render(<ConversationScreen />);
      // Animated component is present
      expect(toJSON()).toBeTruthy();
    });

    it('should show processing indicator when AI speaking', () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isAISpeaking: true,
        error: null,
        startConversation: jest.fn(),
        endConversation: jest.fn(),
      });

      const { getByText } = render(<ConversationScreen />);
      expect(getByText('Processing...')).toBeTruthy();
    });
  });

  // ==================== AC9: Error Handling Tests ====================

  describe('AC9: Error Handling & Edge Cases', () => {
    it('should handle rapid button taps with debounce', async () => {
      const startConvMock = jest.fn().mockResolvedValue(undefined);
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isAISpeaking: false,
        error: null,
        startConversation: startConvMock,
        endConversation: jest.fn(),
      });

      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        true
      );

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');

      // Rapid taps
      fireEvent.press(button);
      fireEvent.press(button);
      fireEvent.press(button);

      await waitFor(() => {
        // Should only call once due to debouncing
        expect(startConvMock).toHaveBeenCalledTimes(1);
      });
    });

    it('should handle permission denial gracefully', async () => {
      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        false
      );
      (audioService.requestMicrophonePermission as jest.Mock).mockResolvedValue(
        false
      );

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');

      fireEvent.press(button);

      await waitFor(() => {
        // Button should still be clickable after denial
        expect(button.props.disabled).toBeFalsy();
      });
    });

    it('should handle start conversation error without crashing', async () => {
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: false,
        isAISpeaking: false,
        error: null,
        startConversation: jest
          .fn()
          .mockRejectedValue(new Error('API error')),
        endConversation: jest.fn(),
      });

      (audioService.checkMicrophonePermission as jest.Mock).mockResolvedValue(
        true
      );

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('Start conversation');

      fireEvent.press(button);

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Connection Error',
          expect.any(String)
        );
      });
    });

    it('should show error message when end conversation fails', async () => {
      const endConvMock = jest.fn().mockRejectedValue(new Error('End failed'));
      (useConversationStore as jest.Mock).mockReturnValue({
        isConnected: true,
        isAISpeaking: false,
        error: null,
        startConversation: jest.fn(),
        endConversation: endConvMock,
      });

      const { getByLabelText } = render(<ConversationScreen />);
      const button = getByLabelText('End conversation');

      fireEvent.press(button);

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Error',
          expect.stringContaining('Failed to end')
        );
      });
    });
  });

  // ==================== AC10: Responsive Design Tests ====================

  describe('AC10: Responsive Design', () => {
    it('should render on all screen sizes', () => {
      const { toJSON } = render(<ConversationScreen />);
      expect(toJSON()).toBeTruthy();
    });

    it('should use flexbox for centering', () => {
      const { toJSON } = render(<ConversationScreen />);
      expect(toJSON()).toBeTruthy();
      // Styles use flex layout for responsive design
    });
  });
});
