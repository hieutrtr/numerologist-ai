import { renderHook, act, waitFor } from '@testing-library/react-native';
import { useConversationStore } from '../../src/stores/useConversationStore';

/**
 * Mock dependencies
 */
jest.mock('../../src/services/api', () => ({
  apiClient: {
    post: jest.fn(),
  },
}));

jest.mock('@daily-co/daily-js', () => ({
  default: {
    createCallObject: jest.fn(),
  },
}));

import { apiClient } from '../../src/services/api';

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('useConversationStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state values', () => {
      const { result } = renderHook(() => useConversationStore());

      expect(result.current.conversationId).toBeNull();
      expect(result.current.dailyCall).toBeNull();
      expect(result.current.isConnected).toBe(false);
      expect(result.current.isMicActive).toBe(false);
      expect(result.current.isAISpeaking).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should have all required actions', () => {
      const { result } = renderHook(() => useConversationStore());

      expect(typeof result.current.startConversation).toBe('function');
      expect(typeof result.current.endConversation).toBe('function');
      expect(typeof result.current.toggleMic).toBe('function');
    });
  });

  describe('startConversation()', () => {
    it('should call backend API with correct endpoint', async () => {
      const mockResponse = {
        data: {
          conversation_id: 'test-conv-id-123',
          daily_room_url: 'https://example.daily.co/test-room',
          daily_token: 'test-token-abc123',
        },
      };
      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useConversationStore());

      // Mock Daily.co SDK
      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn(),
        setLocalAudio: jest.fn(),
      };

      const DailyIframe = require('@daily-co/daily-js').default;
      DailyIframe.createCallObject.mockReturnValue(mockCallFrame);

      await act(async () => {
        await result.current.startConversation();
      });

      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/v1/conversations/start'
      );
    });

    it('should create Daily.co call object and join room', async () => {
      const mockResponse = {
        data: {
          conversation_id: 'test-conv-id-123',
          daily_room_url: 'https://example.daily.co/test-room',
          daily_token: 'test-token-abc123',
        },
      };
      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useConversationStore());

      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn(),
        setLocalAudio: jest.fn(),
      };

      const DailyIframe = require('@daily-co/daily-js').default;
      DailyIframe.createCallObject.mockReturnValue(mockCallFrame);

      await act(async () => {
        await result.current.startConversation();
      });

      expect(DailyIframe.createCallObject).toHaveBeenCalled();
      expect(mockCallFrame.join).toHaveBeenCalledWith({
        url: 'https://example.daily.co/test-room',
        token: 'test-token-abc123',
      });
    });

    it('should update state with connection details on success', async () => {
      const mockResponse = {
        data: {
          conversation_id: 'test-conv-id-123',
          daily_room_url: 'https://example.daily.co/test-room',
          daily_token: 'test-token-abc123',
        },
      };
      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useConversationStore());

      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn(),
        setLocalAudio: jest.fn(),
      };

      const DailyIframe = require('@daily-co/daily-js').default;
      DailyIframe.createCallObject.mockReturnValue(mockCallFrame);

      await act(async () => {
        await result.current.startConversation();
      });

      expect(result.current.conversationId).toBe('test-conv-id-123');
      expect(result.current.dailyCall).toBe(mockCallFrame);
      expect(result.current.isConnected).toBe(true);
      expect(result.current.isMicActive).toBe(true);
      expect(result.current.error).toBeNull();
    });

    it('should handle API errors and set error state', async () => {
      const testError = new Error('API request failed');
      mockApiClient.post.mockRejectedValueOnce(testError);

      const { result } = renderHook(() => useConversationStore());

      await act(async () => {
        try {
          await result.current.startConversation();
        } catch (err) {
          // Error is expected
        }
      });

      expect(result.current.error).toBe('API request failed');
      expect(result.current.isConnected).toBe(false);
    });

    it('should re-throw errors after storing in error state', async () => {
      const testError = new Error('Network error');
      mockApiClient.post.mockRejectedValueOnce(testError);

      const { result } = renderHook(() => useConversationStore());

      let thrownError;
      await act(async () => {
        try {
          await result.current.startConversation();
        } catch (err) {
          thrownError = err;
        }
      });

      expect(thrownError).toBe(testError);
    });

    it('should handle Daily.co SDK not installed', async () => {
      mockApiClient.post.mockResolvedValueOnce({
        data: {
          conversation_id: 'test-conv-id',
          daily_room_url: 'https://example.daily.co/test',
          daily_token: 'token',
        },
      });

      const { result } = renderHook(() => useConversationStore());

      // Mock import failure
      const originalImport = global.require;
      jest.doMock('@daily-co/daily-js', () => {
        throw new Error('Cannot find module');
      });

      await act(async () => {
        try {
          await result.current.startConversation();
        } catch (err) {
          // Expected error
        }
      });

      // Check that error message mentions SDK installation
      expect(result.current.error).toContain('Daily.co SDK');
    });
  });

  describe('endConversation()', () => {
    it('should leave Daily.co room if call exists', async () => {
      const { result } = renderHook(() => useConversationStore());

      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn(),
        setLocalAudio: jest.fn(),
      };

      // Set up state with active call
      act(() => {
        useConversationStore.setState({
          dailyCall: mockCallFrame,
          conversationId: 'test-conv-id',
          isConnected: true,
        });
      });

      await act(async () => {
        await result.current.endConversation();
      });

      expect(mockCallFrame.leave).toHaveBeenCalled();
      expect(mockCallFrame.destroy).toHaveBeenCalled();
    });

    it('should call backend end endpoint if conversationId exists', async () => {
      mockApiClient.post.mockResolvedValueOnce({
        message: 'Conversation ended',
        duration_seconds: 120,
      });

      const { result } = renderHook(() => useConversationStore());

      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn(),
        setLocalAudio: jest.fn(),
      };

      act(() => {
        useConversationStore.setState({
          dailyCall: mockCallFrame,
          conversationId: 'test-conv-id-123',
          isConnected: true,
        });
      });

      await act(async () => {
        await result.current.endConversation();
      });

      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/v1/conversations/test-conv-id-123/end'
      );
    });

    it('should reset state after ending conversation', async () => {
      mockApiClient.post.mockResolvedValueOnce({
        message: 'Conversation ended',
      });

      const { result } = renderHook(() => useConversationStore());

      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn(),
        setLocalAudio: jest.fn(),
      };

      act(() => {
        useConversationStore.setState({
          dailyCall: mockCallFrame,
          conversationId: 'test-conv-id',
          isConnected: true,
          isMicActive: true,
          error: null,
        });
      });

      await act(async () => {
        await result.current.endConversation();
      });

      expect(result.current.conversationId).toBeNull();
      expect(result.current.dailyCall).toBeNull();
      expect(result.current.isConnected).toBe(false);
      expect(result.current.isMicActive).toBe(false);
      expect(result.current.isAISpeaking).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should be no-op when no active call exists', async () => {
      const { result } = renderHook(() => useConversationStore());

      // Verify initial state
      expect(result.current.dailyCall).toBeNull();
      expect(result.current.conversationId).toBeNull();

      await act(async () => {
        await result.current.endConversation();
      });

      // State should still be clean
      expect(result.current.isConnected).toBe(false);
      expect(mockApiClient.post).not.toHaveBeenCalled();
    });

    it('should handle errors gracefully without re-throwing', async () => {
      const testError = new Error('Backend error');
      mockApiClient.post.mockRejectedValueOnce(testError);

      const { result } = renderHook(() => useConversationStore());

      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn().mockImplementation(() => {
          throw new Error('Destroy failed');
        }),
        setLocalAudio: jest.fn(),
      };

      act(() => {
        useConversationStore.setState({
          dailyCall: mockCallFrame,
          conversationId: 'test-conv-id',
        });
      });

      let errorThrown = false;
      await act(async () => {
        try {
          await result.current.endConversation();
        } catch (err) {
          errorThrown = true;
        }
      });

      // Should NOT throw
      expect(errorThrown).toBe(false);
    });
  });

  describe('toggleMic()', () => {
    it('should toggle microphone state when call exists', () => {
      const { result } = renderHook(() => useConversationStore());

      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn(),
        setLocalAudio: jest.fn(),
      };

      act(() => {
        useConversationStore.setState({
          dailyCall: mockCallFrame,
          isMicActive: true,
          isConnected: true,
        });
      });

      act(() => {
        result.current.toggleMic();
      });

      expect(mockCallFrame.setLocalAudio).toHaveBeenCalledWith(false);
      expect(result.current.isMicActive).toBe(false);
    });

    it('should toggle microphone from off to on', () => {
      const { result } = renderHook(() => useConversationStore());

      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn(),
        setLocalAudio: jest.fn(),
      };

      act(() => {
        useConversationStore.setState({
          dailyCall: mockCallFrame,
          isMicActive: false,
          isConnected: true,
        });
      });

      act(() => {
        result.current.toggleMic();
      });

      expect(mockCallFrame.setLocalAudio).toHaveBeenCalledWith(true);
      expect(result.current.isMicActive).toBe(true);
    });

    it('should be no-op when no call exists', () => {
      const { result } = renderHook(() => useConversationStore());

      expect(result.current.dailyCall).toBeNull();

      // Should not throw
      act(() => {
        result.current.toggleMic();
      });

      expect(result.current.isMicActive).toBe(false);
    });

    it('should handle SDK errors gracefully', () => {
      const { result } = renderHook(() => useConversationStore());

      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn(),
        setLocalAudio: jest.fn().mockImplementation(() => {
          throw new Error('SDK error');
        }),
      };

      act(() => {
        useConversationStore.setState({
          dailyCall: mockCallFrame,
          isMicActive: true,
          isConnected: true,
        });
      });

      // Should not throw
      expect(() => {
        act(() => {
          result.current.toggleMic();
        });
      }).not.toThrow();

      // State should not change on SDK error
      expect(result.current.isMicActive).toBe(true);
    });
  });

  describe('Store Type Safety', () => {
    it('should export ConversationState type', () => {
      // Type check at compile time - this test verifies the type exports exist
      const state: ReturnType<typeof useConversationStore> = useConversationStore(
        (state) => state
      );

      expect(state).toBeDefined();
      expect(typeof state.startConversation).toBe('function');
      expect(typeof state.endConversation).toBe('function');
      expect(typeof state.toggleMic).toBe('function');
    });
  });

  describe('Integration Tests', () => {
    it('should handle complete conversation lifecycle', async () => {
      const mockResponse = {
        data: {
          conversation_id: 'test-conv-id-123',
          daily_room_url: 'https://example.daily.co/test-room',
          daily_token: 'test-token-abc123',
        },
      };
      mockApiClient.post.mockResolvedValueOnce(mockResponse);
      mockApiClient.post.mockResolvedValueOnce({
        message: 'Conversation ended',
      });

      const { result } = renderHook(() => useConversationStore());

      const mockCallFrame = {
        join: jest.fn().mockResolvedValue(undefined),
        leave: jest.fn().mockResolvedValue(undefined),
        destroy: jest.fn(),
        setLocalAudio: jest.fn(),
      };

      const DailyIframe = require('@daily-co/daily-js').default;
      DailyIframe.createCallObject.mockReturnValue(mockCallFrame);

      // 1. Start conversation
      await act(async () => {
        await result.current.startConversation();
      });

      expect(result.current.isConnected).toBe(true);
      expect(result.current.conversationId).toBe('test-conv-id-123');

      // 2. Toggle microphone
      act(() => {
        result.current.toggleMic();
      });

      expect(result.current.isMicActive).toBe(false);
      expect(mockCallFrame.setLocalAudio).toHaveBeenCalledWith(false);

      // 3. Toggle microphone again
      act(() => {
        result.current.toggleMic();
      });

      expect(result.current.isMicActive).toBe(true);

      // 4. End conversation
      await act(async () => {
        await result.current.endConversation();
      });

      expect(result.current.isConnected).toBe(false);
      expect(result.current.conversationId).toBeNull();
    });
  });
});
