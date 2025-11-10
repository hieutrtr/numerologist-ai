/**
 * Tests for Daily.co Service
 *
 * Unit tests for daily.service.ts covering:
 * - Call object initialization and configuration
 * - Room joining with credentials
 * - Event listener setup and cleanup
 * - Audio configuration for different platforms
 * - Error handling and user-friendly messages
 * - Participant tracking
 */

import * as dailyService from '../../src/services/daily.service';

/**
 * Mock Daily.co SDK
 */
jest.mock('@daily-co/react-native-daily-js', () => {
  return {
    __esModule: true,
    default: {
      createCallObject: jest.fn(),
    },
  };
});

/**
 * Mock React Native Platform
 */
jest.mock('react-native', () => ({
  Platform: {
    OS: 'android',
  },
}));

describe('Daily.co Service', () => {
  let mockCall: any;
  let mockDailySDK: any;

  beforeEach(() => {
    jest.clearAllMocks();

    // Create mock call object with all required methods
    mockCall = {
      join: jest.fn().mockResolvedValue({}),
      leave: jest.fn().mockResolvedValue({}),
      destroy: jest.fn(),
      on: jest.fn(),
      off: jest.fn(),
      getParticipants: jest.fn().mockReturnValue({}),
      getParticipantCount: jest.fn().mockReturnValue(0),
      setAudioInputEnabled: jest.fn().mockResolvedValue({}),
      setAudioOutputEnabled: jest.fn().mockResolvedValue({}),
      setLocalAudio: jest.fn(),
    };

    // Mock Daily SDK
    mockDailySDK = require('@daily-co/react-native-daily-js').default;
    mockDailySDK.createCallObject.mockResolvedValue(mockCall);

    // Suppress console logs during tests
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  // ===================== AC1: SDK Installation Tests =====================

  describe('initializeCall - AC1: SDK Installation', () => {
    it('should create a call object with proper configuration', async () => {
      const call = await dailyService.initializeCall();

      expect(mockDailySDK.createCallObject).toHaveBeenCalledWith({
        videoSource: false,
        audioSource: true,
        audioOutput: true,
        receiveSettings: {
          screenVideo: {
            subscribeToAll: false,
          },
        },
      });

      expect(call).toBe(mockCall);
    });

    it('should throw error if call object creation fails', async () => {
      mockDailySDK.createCallObject.mockResolvedValue(null);

      await expect(dailyService.initializeCall()).rejects.toThrow(
        'Failed to create Daily call object'
      );
    });

    it('should handle SDK not being available', async () => {
      mockDailySDK.createCallObject.mockRejectedValue(
        new Error('SDK not available')
      );

      await expect(dailyService.initializeCall()).rejects.toThrow();
    });
  });

  // ===================== AC2: Call Object Tests =====================

  describe('configureAudio - AC2 & AC4: Audio Configuration', () => {
    it('should configure audio with default settings', async () => {
      await dailyService.configureAudio(mockCall);

      expect(mockCall.setAudioInputEnabled).toHaveBeenCalledWith(true);
      expect(mockCall.setAudioOutputEnabled).toHaveBeenCalledWith(true);
    });

    it('should configure audio with custom settings', async () => {
      await dailyService.configureAudio(mockCall, {
        audioInputEnabled: false,
        audioOutputEnabled: true,
      });

      expect(mockCall.setAudioInputEnabled).toHaveBeenCalledWith(false);
      expect(mockCall.setAudioOutputEnabled).toHaveBeenCalledWith(true);
    });

    it('should handle audio configuration errors', async () => {
      mockCall.setAudioInputEnabled.mockRejectedValue(
        new Error('Permission denied')
      );

      await expect(
        dailyService.configureAudio(mockCall)
      ).rejects.toThrow('Audio configuration failed');
    });
  });

  // ===================== AC3: Room Joining Tests =====================

  describe('joinRoom - AC3: Joining Rooms', () => {
    const validCredentials = {
      roomUrl: 'https://example.daily.co/abc123',
      token: 'valid-token-123',
    };

    it('should join room with valid credentials', async () => {
      await dailyService.joinRoom(mockCall, validCredentials);

      expect(mockCall.join).toHaveBeenCalledWith({
        url: validCredentials.roomUrl,
        token: validCredentials.token,
      });
    });

    it('should join room without token if not provided', async () => {
      const credentialsWithoutToken = {
        roomUrl: 'https://example.daily.co/abc123',
        token: '',
      };

      await dailyService.joinRoom(mockCall, credentialsWithoutToken);

      expect(mockCall.join).toHaveBeenCalledWith({
        url: credentialsWithoutToken.roomUrl,
      });
    });

    it('should throw error if room URL is missing', async () => {
      const invalidCredentials = {
        roomUrl: '',
        token: 'valid-token',
      };

      await expect(
        dailyService.joinRoom(mockCall, invalidCredentials)
      ).rejects.toThrow('Room URL is required');
    });

    it('should throw error if room URL is invalid format', async () => {
      const invalidCredentials = {
        roomUrl: 'not-a-url',
        token: 'valid-token',
      };

      await expect(
        dailyService.joinRoom(mockCall, invalidCredentials)
      ).rejects.toThrow('Invalid room URL format');
    });

    it('should map network errors to user-friendly messages', async () => {
      mockCall.join.mockRejectedValue(new Error('Network timeout'));

      await expect(
        dailyService.joinRoom(mockCall, validCredentials)
      ).rejects.toThrow('Network error - check your connection');
    });

    it('should map expired room error to user-friendly message', async () => {
      mockCall.join.mockRejectedValue(new Error('Room expired'));

      await expect(
        dailyService.joinRoom(mockCall, validCredentials)
      ).rejects.toThrow('Room expired or no longer available');
    });
  });

  // ===================== AC6 & AC7: Event Handler Tests =====================

  describe('setupCallListeners - AC6 & AC7: Event Handlers', () => {
    const mockCallbacks = {
      onConnected: jest.fn(),
      onDisconnected: jest.fn(),
      onError: jest.fn(),
      onParticipantJoined: jest.fn(),
      onParticipantLeft: jest.fn(),
      onNetworkQuality: jest.fn(),
    };

    it('should setup all event listeners', () => {
      const cleanup = dailyService.setupCallListeners(mockCall, mockCallbacks);

      expect(mockCall.on).toHaveBeenCalledWith('joined-meeting', expect.any(Function));
      expect(mockCall.on).toHaveBeenCalledWith('left-meeting', expect.any(Function));
      expect(mockCall.on).toHaveBeenCalledWith('error', expect.any(Function));
      expect(mockCall.on).toHaveBeenCalledWith('participant-joined', expect.any(Function));
      expect(mockCall.on).toHaveBeenCalledWith('participant-left', expect.any(Function));
      expect(mockCall.on).toHaveBeenCalledWith('network-quality-change', expect.any(Function));

      expect(cleanup).toBeInstanceOf(Function);
    });

    it('should trigger onConnected callback', () => {
      const cleanup = dailyService.setupCallListeners(mockCall, mockCallbacks);

      // Get the handler function that was registered
      const joinedHandler = mockCall.on.mock.calls.find(
        (call: any[]) => call[0] === 'joined-meeting'
      )[1];

      joinedHandler();

      expect(mockCallbacks.onConnected).toHaveBeenCalled();
    });

    it('should trigger onDisconnected callback', () => {
      const cleanup = dailyService.setupCallListeners(mockCall, mockCallbacks);

      const leftHandler = mockCall.on.mock.calls.find(
        (call: any[]) => call[0] === 'left-meeting'
      )[1];

      leftHandler();

      expect(mockCallbacks.onDisconnected).toHaveBeenCalled();
    });

    it('should handle participant-joined event', () => {
      const cleanup = dailyService.setupCallListeners(mockCall, mockCallbacks);

      const participantHandler = mockCall.on.mock.calls.find(
        (call: any[]) => call[0] === 'participant-joined'
      )[1];

      participantHandler({
        participant: {
          session_id: 'participant-123',
          name: 'Bot',
          local: false,
          audio: true,
          audioBlock: false,
          video: false,
          videoBlock: true,
        },
      });

      expect(mockCallbacks.onParticipantJoined).toHaveBeenCalledWith(
        expect.objectContaining({
          id: 'participant-123',
          name: 'Bot',
          isLocal: false,
        })
      );
    });

    it('should cleanup listeners when cleanup function is called', () => {
      const cleanup = dailyService.setupCallListeners(mockCall, mockCallbacks);

      cleanup();

      expect(mockCall.off).toHaveBeenCalled();
    });

    it('should handle errors in listener setup gracefully', () => {
      mockCall.on.mockImplementation(() => {
        throw new Error('Setup failed');
      });

      const cleanup = dailyService.setupCallListeners(mockCall, mockCallbacks);

      expect(cleanup).toBeInstanceOf(Function);
    });
  });

  // ===================== AC9: Lifecycle Tests =====================

  describe('teardownCall - AC9: Lifecycle Management', () => {
    it('should leave room and destroy call object', async () => {
      const cleanup = jest.fn();

      await dailyService.teardownCall(mockCall, cleanup);

      expect(mockCall.leave).toHaveBeenCalled();
      expect(mockCall.destroy).toHaveBeenCalled();
      expect(cleanup).toHaveBeenCalled();
    });

    it('should handle leave errors gracefully', async () => {
      mockCall.leave.mockRejectedValue(new Error('Leave failed'));

      await dailyService.teardownCall(mockCall);

      expect(mockCall.destroy).toHaveBeenCalled();
    });

    it('should handle destroy errors gracefully', async () => {
      mockCall.destroy.mockImplementation(() => {
        throw new Error('Destroy failed');
      });

      await dailyService.teardownCall(mockCall);

      // Should not throw
      expect(mockCall.leave).toHaveBeenCalled();
    });

    it('should handle cleanup without listeners', async () => {
      await dailyService.teardownCall(mockCall);

      expect(mockCall.leave).toHaveBeenCalled();
      expect(mockCall.destroy).toHaveBeenCalled();
    });
  });

  // ===================== Utility Function Tests =====================

  describe('getParticipants', () => {
    it('should return list of participants', () => {
      mockCall.getParticipants.mockReturnValue({
        local: {
          session_id: 'local-id',
          local: true,
          audio: true,
          video: false,
        },
        bot: {
          session_id: 'bot-id',
          local: false,
          audio: true,
          name: 'Numerology Bot',
        },
      });

      const participants = dailyService.getParticipants(mockCall);

      expect(participants).toHaveLength(2);
      expect(participants[0].isLocal).toBe(true);
      expect(participants[1].name).toBe('Numerology Bot');
    });

    it('should return empty array if no participants', () => {
      mockCall.getParticipants.mockReturnValue(null);

      const participants = dailyService.getParticipants(mockCall);

      expect(participants).toEqual([]);
    });

    it('should handle errors gracefully', () => {
      mockCall.getParticipants.mockImplementation(() => {
        throw new Error('Failed to get participants');
      });

      const participants = dailyService.getParticipants(mockCall);

      expect(participants).toEqual([]);
    });
  });

  describe('isConnected', () => {
    it('should return true if call has participants', () => {
      mockCall.getParticipants.mockReturnValue({
        local: { session_id: 'local-id' },
      });

      const connected = dailyService.isConnected(mockCall);

      expect(connected).toBe(true);
    });

    it('should return false if no participants', () => {
      mockCall.getParticipants.mockReturnValue({});

      const connected = dailyService.isConnected(mockCall);

      expect(connected).toBe(false);
    });

    it('should return false on error', () => {
      mockCall.getParticipants.mockImplementation(() => {
        throw new Error('Error');
      });

      const connected = dailyService.isConnected(mockCall);

      expect(connected).toBe(false);
    });
  });

  // ===================== Integration Tests =====================

  describe('Integration: Full conversation flow', () => {
    it('should handle complete conversation lifecycle', async () => {
      const callbacks = {
        onConnected: jest.fn(),
        onDisconnected: jest.fn(),
      };

      // 1. Initialize
      const call = await dailyService.initializeCall();
      expect(call).toBe(mockCall);

      // 2. Configure audio
      await dailyService.configureAudio(call);
      expect(mockCall.setAudioInputEnabled).toHaveBeenCalled();

      // 3. Setup listeners
      const cleanup = dailyService.setupCallListeners(call, callbacks);
      expect(mockCall.on).toHaveBeenCalled();

      // 4. Join room
      await dailyService.joinRoom(call, {
        roomUrl: 'https://example.daily.co/abc',
        token: 'token123',
      });
      expect(mockCall.join).toHaveBeenCalled();

      // 5. Simulate connection
      const joinedHandler = mockCall.on.mock.calls.find(
        (call: any[]) => call[0] === 'joined-meeting'
      )[1];
      joinedHandler();
      expect(callbacks.onConnected).toHaveBeenCalled();

      // 6. Teardown
      await dailyService.teardownCall(call, cleanup);
      expect(mockCall.leave).toHaveBeenCalled();
      expect(mockCall.destroy).toHaveBeenCalled();
    });
  });
});
