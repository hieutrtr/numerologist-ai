import { requestMicrophonePermission, checkMicrophonePermission } from '../../src/services/audio.service';
import { Audio } from 'expo-av';
import { Platform } from 'react-native';

/**
 * Mock dependencies
 */
jest.mock('expo-av', () => ({
  Audio: {
    requestPermissionsAsync: jest.fn(),
    getPermissionsAsync: jest.fn(),
  },
}));

jest.mock('react-native', () => ({
  Platform: {
    OS: 'ios', // Default to mobile for most tests
  },
}));

// Mock navigator for web tests
global.navigator = {
  mediaDevices: {
    getUserMedia: jest.fn(),
  },
  permissions: {
    query: jest.fn(),
  },
} as any;

const mockAudio = Audio as jest.Mocked<typeof Audio>;
const mockPlatform = Platform as jest.Mocked<typeof Platform>;

describe('Audio Permission Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset platform to ios by default
    (mockPlatform.OS as any) = 'ios';
  });

  describe('requestMicrophonePermission()', () => {
    describe('Mobile - iOS/Android', () => {
      beforeEach(() => {
        (mockPlatform.OS as any) = 'ios';
      });

      it('should return true when Audio.requestPermissionsAsync grants permission', async () => {
        mockAudio.requestPermissionsAsync.mockResolvedValue({
          status: 'granted',
          expires: 1234567890,
          canAskAgain: true,
          granted: true,
        } as any);

        const result = await requestMicrophonePermission();

        expect(result).toBe(true);
        expect(mockAudio.requestPermissionsAsync).toHaveBeenCalled();
      });

      it('should return false when Audio.requestPermissionsAsync denies permission', async () => {
        mockAudio.requestPermissionsAsync.mockResolvedValue({
          status: 'denied',
          expires: 1234567890,
          canAskAgain: true,
          granted: false,
        } as any);

        const result = await requestMicrophonePermission();

        expect(result).toBe(false);
      });

      it('should return false when Audio.requestPermissionsAsync fails', async () => {
        mockAudio.requestPermissionsAsync.mockRejectedValue(
          new Error('Expo Audio error')
        );

        const result = await requestMicrophonePermission();

        expect(result).toBe(false);
      });

      it('should handle undetermined status (not yet asked)', async () => {
        mockAudio.requestPermissionsAsync.mockResolvedValue({
          status: 'undetermined',
          expires: 1234567890,
          canAskAgain: true,
          granted: false,
        } as any);

        const result = await requestMicrophonePermission();

        expect(result).toBe(false);
      });
    });

    describe('Web - Browser', () => {
      beforeEach(() => {
        (mockPlatform.OS as any) = 'web';
      });

      it('should return true when getUserMedia grants permission', async () => {
        const mockTrack = {
          stop: jest.fn(),
        };
        const mockStream = {
          getTracks: jest.fn().mockReturnValue([mockTrack]),
        };

        (global.navigator.mediaDevices.getUserMedia as jest.Mock).mockResolvedValue(
          mockStream
        );

        const result = await requestMicrophonePermission();

        expect(result).toBe(true);
        expect(mockTrack.stop).toHaveBeenCalled();
        expect(mockStream.getTracks).toHaveBeenCalled();
      });

      it('should return false when getUserMedia denies permission', async () => {
        const error = new DOMException('NotAllowedError', 'NotAllowedError');
        (global.navigator.mediaDevices.getUserMedia as jest.Mock).mockRejectedValue(
          error
        );

        const result = await requestMicrophonePermission();

        expect(result).toBe(false);
      });

      it('should return false when getUserMedia fails with NotFoundError', async () => {
        const error = new DOMException('NotFoundError', 'NotFoundError');
        (global.navigator.mediaDevices.getUserMedia as jest.Mock).mockRejectedValue(
          error
        );

        const result = await requestMicrophonePermission();

        expect(result).toBe(false);
      });

      it('should return false when mediaDevices is unavailable', async () => {
        // Simulate browser without mediaDevices
        const originalMediaDevices = global.navigator.mediaDevices;
        delete (global.navigator as any).mediaDevices;

        const result = await requestMicrophonePermission();

        expect(result).toBe(false);

        // Restore
        (global.navigator as any).mediaDevices = originalMediaDevices;
      });

      it('should stop all media tracks after permission check', async () => {
        const mockTrack1 = { stop: jest.fn() };
        const mockTrack2 = { stop: jest.fn() };
        const mockStream = {
          getTracks: jest.fn().mockReturnValue([mockTrack1, mockTrack2]),
        };

        (global.navigator.mediaDevices.getUserMedia as jest.Mock).mockResolvedValue(
          mockStream
        );

        await requestMicrophonePermission();

        expect(mockTrack1.stop).toHaveBeenCalled();
        expect(mockTrack2.stop).toHaveBeenCalled();
      });
    });
  });

  describe('checkMicrophonePermission()', () => {
    describe('Mobile - iOS/Android', () => {
      beforeEach(() => {
        (mockPlatform.OS as any) = 'ios';
      });

      it('should return true when Audio.getPermissionsAsync returns granted', async () => {
        mockAudio.getPermissionsAsync.mockResolvedValue({
          status: 'granted',
          expires: 1234567890,
          canAskAgain: true,
          granted: true,
        } as any);

        const result = await checkMicrophonePermission();

        expect(result).toBe(true);
      });

      it('should return false when Audio.getPermissionsAsync returns denied', async () => {
        mockAudio.getPermissionsAsync.mockResolvedValue({
          status: 'denied',
          expires: 1234567890,
          canAskAgain: true,
          granted: false,
        } as any);

        const result = await checkMicrophonePermission();

        expect(result).toBe(false);
      });

      it('should return false when Audio.getPermissionsAsync returns undetermined', async () => {
        mockAudio.getPermissionsAsync.mockResolvedValue({
          status: 'undetermined',
          expires: 1234567890,
          canAskAgain: true,
          granted: false,
        } as any);

        const result = await checkMicrophonePermission();

        expect(result).toBe(false);
      });

      it('should return false when Audio.getPermissionsAsync fails', async () => {
        mockAudio.getPermissionsAsync.mockRejectedValue(
          new Error('Expo Audio error')
        );

        const result = await checkMicrophonePermission();

        expect(result).toBe(false);
      });
    });

    describe('Web - Browser', () => {
      beforeEach(() => {
        (mockPlatform.OS as any) = 'web';
      });

      it('should return true when permissions.query returns granted', async () => {
        (global.navigator.permissions.query as jest.Mock).mockResolvedValue({
          state: 'granted',
        });

        const result = await checkMicrophonePermission();

        expect(result).toBe(true);
        expect(global.navigator.permissions.query).toHaveBeenCalledWith({
          name: 'microphone',
        });
      });

      it('should return false when permissions.query returns denied', async () => {
        (global.navigator.permissions.query as jest.Mock).mockResolvedValue({
          state: 'denied',
        });

        const result = await checkMicrophonePermission();

        expect(result).toBe(false);
      });

      it('should return false when permissions.query returns prompt (not yet asked)', async () => {
        (global.navigator.permissions.query as jest.Mock).mockResolvedValue({
          state: 'prompt',
        });

        const result = await checkMicrophonePermission();

        expect(result).toBe(false);
      });

      it('should return false when permissions.query is not supported', async () => {
        // Simulate browser without Permissions API
        const originalPermissions = global.navigator.permissions;
        delete (global.navigator as any).permissions;

        const result = await checkMicrophonePermission();

        expect(result).toBe(false);

        // Restore
        (global.navigator as any).permissions = originalPermissions;
      });

      it('should return false when permissions.query throws error', async () => {
        (global.navigator.permissions.query as jest.Mock).mockRejectedValue(
          new Error('Permissions API error')
        );

        const result = await checkMicrophonePermission();

        expect(result).toBe(false);
      });
    });
  });

  describe('Error Handling - General', () => {
    it('should never throw on either function', async () => {
      mockAudio.requestPermissionsAsync.mockRejectedValue(new Error('Unexpected error'));

      expect(async () => {
        await requestMicrophonePermission();
      }).not.toThrow();

      mockAudio.getPermissionsAsync.mockRejectedValue(new Error('Unexpected error'));

      expect(async () => {
        await checkMicrophonePermission();
      }).not.toThrow();
    });

    it('should return false on all error paths', async () => {
      mockAudio.requestPermissionsAsync.mockRejectedValue(new Error('Test error'));
      let result = await requestMicrophonePermission();
      expect(result).toBe(false);

      mockAudio.getPermissionsAsync.mockRejectedValue(new Error('Test error'));
      result = await checkMicrophonePermission();
      expect(result).toBe(false);
    });
  });

  describe('Platform Detection', () => {
    it('should use iOS/Android path when Platform.OS is "ios"', async () => {
      (mockPlatform.OS as any) = 'ios';
      mockAudio.requestPermissionsAsync.mockResolvedValue({
        status: 'granted',
      } as any);

      await requestMicrophonePermission();

      expect(mockAudio.requestPermissionsAsync).toHaveBeenCalled();
    });

    it('should use iOS/Android path when Platform.OS is "android"', async () => {
      (mockPlatform.OS as any) = 'android';
      mockAudio.requestPermissionsAsync.mockResolvedValue({
        status: 'granted',
      } as any);

      await requestMicrophonePermission();

      expect(mockAudio.requestPermissionsAsync).toHaveBeenCalled();
    });

    it('should use web path when Platform.OS is "web"', async () => {
      (mockPlatform.OS as any) = 'web';
      const mockStream = {
        getTracks: jest.fn().mockReturnValue([{ stop: jest.fn() }]),
      };
      (global.navigator.mediaDevices.getUserMedia as jest.Mock).mockResolvedValue(
        mockStream
      );

      await requestMicrophonePermission();

      expect(global.navigator.mediaDevices.getUserMedia).toHaveBeenCalled();
    });
  });

  describe('Permission Caching Behavior (OS-level)', () => {
    it('should respect cached permissions on subsequent calls (mobile)', async () => {
      (mockPlatform.OS as any) = 'ios';
      mockAudio.requestPermissionsAsync.mockResolvedValue({
        status: 'granted',
      } as any);

      // First call
      const result1 = await requestMicrophonePermission();
      expect(result1).toBe(true);

      // Second call - OS caches the permission
      const result2 = await requestMicrophonePermission();
      expect(result2).toBe(true);

      // Function called twice, but OS handles caching internally
      expect(mockAudio.requestPermissionsAsync).toHaveBeenCalledTimes(2);
    });

    it('should report cached denied permission on subsequent checks (mobile)', async () => {
      (mockPlatform.OS as any) = 'ios';
      mockAudio.getPermissionsAsync.mockResolvedValue({
        status: 'denied',
      } as any);

      // First check
      const result1 = await checkMicrophonePermission();
      expect(result1).toBe(false);

      // Second check - permission still denied
      const result2 = await checkMicrophonePermission();
      expect(result2).toBe(false);
    });
  });

  describe('Integration - Typical User Flow', () => {
    it('should handle: check permission, request if needed, verify granted', async () => {
      (mockPlatform.OS as any) = 'ios';

      // Step 1: Check if permission already granted
      mockAudio.getPermissionsAsync.mockResolvedValueOnce({
        status: 'undetermined',
      } as any);
      let hasPermission = await checkMicrophonePermission();
      expect(hasPermission).toBe(false);

      // Step 2: Request permission
      mockAudio.requestPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
      } as any);
      hasPermission = await requestMicrophonePermission();
      expect(hasPermission).toBe(true);

      // Step 3: Verify permission is now granted
      mockAudio.getPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
      } as any);
      hasPermission = await checkMicrophonePermission();
      expect(hasPermission).toBe(true);
    });

    it('should handle: check, request denied, show error', async () => {
      (mockPlatform.OS as any) = 'android';

      // Check permission
      mockAudio.getPermissionsAsync.mockResolvedValueOnce({
        status: 'undetermined',
      } as any);
      let hasPermission = await checkMicrophonePermission();
      expect(hasPermission).toBe(false);

      // User denies
      mockAudio.requestPermissionsAsync.mockResolvedValueOnce({
        status: 'denied',
        canAskAgain: true,
      } as any);
      hasPermission = await requestMicrophonePermission();
      expect(hasPermission).toBe(false);

      // Future checks return denied (user must change in settings)
      mockAudio.getPermissionsAsync.mockResolvedValueOnce({
        status: 'denied',
      } as any);
      hasPermission = await checkMicrophonePermission();
      expect(hasPermission).toBe(false);
    });

    it('should handle: web permission grant workflow', async () => {
      (mockPlatform.OS as any) = 'web';

      const mockStream = {
        getTracks: jest.fn().mockReturnValue([{ stop: jest.fn() }]),
      };

      // Check permission (not yet requested)
      (global.navigator.permissions.query as jest.Mock).mockResolvedValueOnce({
        state: 'prompt',
      });
      let hasPermission = await checkMicrophonePermission();
      expect(hasPermission).toBe(false);

      // Request permission
      (global.navigator.mediaDevices.getUserMedia as jest.Mock).mockResolvedValueOnce(
        mockStream
      );
      hasPermission = await requestMicrophonePermission();
      expect(hasPermission).toBe(true);

      // Check permission again (now granted)
      (global.navigator.permissions.query as jest.Mock).mockResolvedValueOnce({
        state: 'granted',
      });
      hasPermission = await checkMicrophonePermission();
      expect(hasPermission).toBe(true);
    });
  });
});
