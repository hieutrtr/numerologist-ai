import { Audio } from 'expo-av';
import { Platform } from 'react-native';

/**
 * Service for managing microphone permissions across web and mobile platforms.
 *
 * **Purpose**: Provides a cross-platform API for requesting and checking microphone permissions
 * used for voice conversations.
 *
 * **Design Principles**:
 * - **Platform-specific**: Uses native APIs for each platform (browser APIs for web, Expo Audio for mobile)
 * - **Non-intrusive**: Permission requests only happen when needed (not at app startup)
 * - **Stateless**: Pure functions that query OS state, no internal state management
 * - **Error-safe**: Always returns boolean, never throws (returns false on error)
 * - **Resource-safe**: Immediately stops any media streams obtained during permission checks
 *
 * **Web Implementation**:
 * - Uses `navigator.mediaDevices.getUserMedia()` for permission request
 * - Uses `navigator.permissions.query()` for permission status check
 * - Browser shows native permission prompt (Chrome, Firefox, Safari, Edge)
 * - Automatically stops media stream after checking permission
 *
 * **Mobile Implementation**:
 * - Uses Expo Audio API (`Audio.requestPermissionsAsync()` and `Audio.getPermissionsAsync()`)
 * - Integrates with native iOS/Android permission dialogs
 * - iOS: Uses AVAudioSession for microphone setup
 * - Android: Requests RECORD_AUDIO permission, respects "Don't Ask Again"
 *
 * @example
 * ```typescript
 * import { checkMicrophonePermission, requestMicrophonePermission } from '@/services/audio.service';
 *
 * // Check if permission already granted
 * const hasPermission = await checkMicrophonePermission();
 *
 * // If not, request it
 * if (!hasPermission) {
 *   const granted = await requestMicrophonePermission();
 *   if (!granted) {
 *     Alert.alert('Microphone Required', 'Please enable microphone in settings');
 *   }
 * }
 *
 * // Proceed with voice conversation
 * if (granted) {
 *   await startConversation();
 * }
 * ```
 */

/**
 * Request microphone permission from the user.
 *
 * Shows native permission dialog on first call. Subsequent calls may not show dialog if:
 * - Permission already granted (cached by OS)
 * - User denied permission (user must change in settings)
 *
 * **Web Platform**:
 * - Calls `navigator.mediaDevices.getUserMedia({ audio: true })`
 * - Browser shows native permission prompt
 * - Immediately stops the obtained media stream (only needed permission, not to record)
 * - Returns false if browser doesn't support mediaDevices API
 *
 * **Mobile Platform**:
 * - Calls `Audio.requestPermissionsAsync()`
 * - Shows native iOS/Android permission dialog on first call
 * - iOS: User sees "Allow/Don't Allow" for microphone access
 * - Android: User sees permission dialog; can select "Don't Ask Again"
 *
 * @returns `Promise<boolean>`
 * - `true` if permission granted (user allowed access)
 * - `false` if permission denied or error occurred (including cancellation)
 *
 * @throws Never throws - all errors are caught and return false
 *
 * @example
 * ```typescript
 * const granted = await requestMicrophonePermission();
 * if (granted) {
 *   console.log('Microphone permission granted');
 *   await startConversation();
 * } else {
 *   Alert.alert(
 *     'Microphone Required',
 *     'Microphone is required to use voice conversations. Please enable it in app settings.'
 *   );
 * }
 * ```
 */
export const requestMicrophonePermission = async (): Promise<boolean> => {
  try {
    if (Platform.OS === 'web') {
      // Web: Use browser's native getUserMedia API to request permission
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Permission granted - immediately stop all tracks to clean up
        // (we only needed permission, not to actually record)
        stream.getTracks().forEach((track) => track.stop());
        return true;
      } catch (error) {
        // User denied or error occurred (e.g., no media devices, NotAllowedError, NotFoundError)
        if (__DEV__) {
          console.error('Web microphone permission denied or error:', error);
        }
        return false;
      }
    } else {
      // Mobile: Use Expo Audio API for iOS/Android
      const { status } = await Audio.requestPermissionsAsync();
      return status === 'granted';
    }
  } catch (error) {
    // Outer catch for any unexpected errors
    if (__DEV__) {
      console.error('Error requesting microphone permission:', error);
    }
    return false;
  }
};

/**
 * Check if microphone permission is already granted.
 *
 * **Does NOT show any permission dialogs** - purely checks current status.
 * Useful to determine if we need to call `requestMicrophonePermission()`.
 *
 * **Web Platform**:
 * - Uses `navigator.permissions.query({ name: 'microphone' })`
 * - Returns true only if state === 'granted'
 * - Returns false for 'denied' or 'prompt' (not yet requested)
 * - Gracefully handles browsers that don't support Permissions API
 *
 * **Mobile Platform**:
 * - Uses `Audio.getPermissionsAsync()`
 * - Returns true only if status === 'granted'
 * - Returns false for any other status ('denied', 'undetermined', etc.)
 *
 * @returns `Promise<boolean>`
 * - `true` if permission already granted
 * - `false` if permission denied, not yet requested, or error occurred
 *
 * @throws Never throws - all errors are caught and return false
 *
 * @example
 * ```typescript
 * // Check permission before attempting to start conversation
 * const hasPermission = await checkMicrophonePermission();
 *
 * if (hasPermission) {
 *   // Permission already granted, safe to start conversation
 *   await startConversation();
 * } else {
 *   // Permission not granted, request it
 *   const granted = await requestMicrophonePermission();
 *   if (granted) {
 *     await startConversation();
 *   }
 * }
 * ```
 */
export const checkMicrophonePermission = async (): Promise<boolean> => {
  try {
    if (Platform.OS === 'web') {
      // Web: Check browser permission status using Permissions API
      try {
        const permission = await navigator.permissions?.query?.({
          name: 'microphone',
        });
        return permission?.state === 'granted';
      } catch (error) {
        // Fallback: assume false if Permissions API not supported or fails
        // (some browsers don't support Permissions API)
        if (__DEV__) {
          console.error('Web microphone permission check failed:', error);
        }
        return false;
      }
    } else {
      // Mobile: Check Expo Audio permission status
      const { status } = await Audio.getPermissionsAsync();
      return status === 'granted';
    }
  } catch (error) {
    // Outer catch for any unexpected errors
    if (__DEV__) {
      console.error('Error checking microphone permission:', error);
    }
    return false;
  }
};

/**
 * **Integration with Conversation Store**
 *
 * This service is designed to be called from `useConversationStore` before starting a conversation.
 * The recommended flow in the conversation screen:
 *
 * 1. User taps "Start Conversation" button
 * 2. Screen calls `checkMicrophonePermission()`
 * 3. If not granted, call `requestMicrophonePermission()`
 * 4. If still not granted, show error alert with settings link
 * 5. If granted, call store's `startConversation()` to connect to Daily.co
 *
 * This ensures the user has granted microphone access before we attempt to join the call.
 *
 * @example
 * ```typescript
 * // In conversation screen component:
 * import { checkMicrophonePermission, requestMicrophonePermission } from '@/services/audio.service';
 * import { useConversationStore } from '@/stores/useConversationStore';
 *
 * function ConversationScreen() {
 *   const { startConversation, error } = useConversationStore();
 *
 *   const handleStartPress = async () => {
 *     try {
 *       // 1. Check if permission already granted
 *       let hasPermission = await checkMicrophonePermission();
 *
 *       // 2. If not, request it
 *       if (!hasPermission) {
 *         hasPermission = await requestMicrophonePermission();
 *       }
 *
 *       // 3. If still not granted, show error
 *       if (!hasPermission) {
 *         Alert.alert(
 *           'Microphone Required',
 *           'Microphone access is required to use voice conversations. Please enable it in app settings.'
 *         );
 *         return;
 *       }
 *
 *       // 4. Permission granted, start conversation
 *       await startConversation();
 *     } catch (err) {
 *       Alert.alert('Error', 'Failed to start conversation');
 *     }
 *   };
 *
 *   return (
 *     <View>
 *       <TouchableOpacity onPress={handleStartPress}>
 *         <Text>Start Conversation</Text>
 *       </TouchableOpacity>
 *       {error && <Text style={{color: 'red'}}>{error}</Text>}
 *     </View>
 *   );
 * }
 * ```
 */
