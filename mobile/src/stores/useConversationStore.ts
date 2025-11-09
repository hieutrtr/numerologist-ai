import { create } from 'zustand';
import { apiClient } from '../services/api';

/**
 * Zustand store for managing conversation state and Daily.co integration.
 *
 * Provides:
 * - State tracking for active conversation
 * - API integration with backend conversation endpoints
 * - Daily.co call object lifecycle management
 * - Microphone control
 *
 * Prerequisites:
 * - Backend /api/v1/conversations/start endpoint working (Story 3.4)
 * - Daily.co API keys configured (Story 3.2)
 * - @daily-co/daily-js installed
 *
 * @example
 * // In a React component:
 * import { useConversationStore } from '@/stores/useConversationStore';
 *
 * function ConversationScreen() {
 *   const { isConnected, startConversation, endConversation, toggleMic, error } = useConversationStore();
 *
 *   const handleStart = async () => {
 *     try {
 *       await startConversation();
 *     } catch (err) {
 *       // Error already in store.error
 *     }
 *   };
 *
 *   return (
 *     <View>
 *       {error && <Text style={{color: 'red'}}>{error}</Text>}
 *       <TouchableOpacity onPress={isConnected ? endConversation : handleStart}>
 *         <Text>{isConnected ? 'End Call' : 'Start Call'}</Text>
 *       </TouchableOpacity>
 *     </View>
 *   );
 * }
 */

/**
 * Type definitions for the conversation store state and actions
 */
interface ConversationState {
  // State fields
  conversationId: string | null;
  dailyCall: any | null; // Daily.co call object reference
  isConnected: boolean;
  isMicActive: boolean;
  isAISpeaking: boolean;
  error: string | null;

  // Actions
  startConversation: () => Promise<void>;
  endConversation: () => Promise<void>;
  toggleMic: () => void;
}

/**
 * Backend response type for conversation start endpoint
 */
interface ConversationStartResponse {
  conversation_id: string;
  daily_room_url: string;
  daily_token: string;
}

/**
 * Zustand store hook for conversation state management
 */
export const useConversationStore = create<ConversationState>((set, get) => ({
  // Initial state
  conversationId: null,
  dailyCall: null,
  isConnected: false,
  isMicActive: false,
  isAISpeaking: false,
  error: null,

  /**
   * Action: Start a new conversation
   *
   * Steps:
   * 1. Call backend POST /api/v1/conversations/start endpoint
   * 2. Extract conversation_id, daily_room_url, daily_token from response
   * 3. Create Daily.co call object
   * 4. Join the Daily.co room with provided credentials
   * 5. Update store state with connection details
   *
   * On error:
   * - Catches exception and stores in error state
   * - Re-throws for caller to handle UI feedback
   *
   * @throws Error if backend call fails or Daily.co connection fails
   */
  startConversation: async () => {
    try {
      // Call backend to create conversation and get Daily.co credentials
      const response = await apiClient.post<ConversationStartResponse>(
        '/api/v1/conversations/start'
      );

      const { conversation_id, daily_room_url, daily_token } = response.data;

      // Import Daily.co SDK dynamically to handle optional dependency
      // This allows store to be imported even if Daily.co is not yet installed
      let DailyIframe;
      try {
        // Try to import the Daily.co SDK
        const DailyModule = await import('@daily-co/daily-js');
        DailyIframe = DailyModule.default;
      } catch (importError) {
        throw new Error(
          'Daily.co SDK not installed. Run: npm install @daily-co/daily-js'
        );
      }

      // Create and join Daily.co room
      const callFrame = DailyIframe.createCallObject();

      await callFrame.join({
        url: daily_room_url,
        token: daily_token,
      });

      // Update state with connection details
      set({
        conversationId: conversation_id,
        dailyCall: callFrame,
        isConnected: true,
        isMicActive: true,
        error: null,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      set({ error: errorMessage });
      throw error; // Re-throw for caller to handle
    }
  },

  /**
   * Action: End the current conversation
   *
   * Steps:
   * 1. Get current dailyCall and conversationId from state
   * 2. If dailyCall exists:
   *    - Leave the Daily.co room
   *    - Destroy the call object
   * 3. If conversationId exists:
   *    - Notify backend that conversation is ending
   * 4. Reset all state fields to initial values
   *
   * On error:
   * - Catches exception and stores in error state
   * - Still attempts cleanup even if error occurs
   * - Does not re-throw (cleanup should be best-effort)
   */
  endConversation: async () => {
    const { dailyCall, conversationId } = get();

    try {
      // Clean up Daily.co call
      if (dailyCall) {
        try {
          await dailyCall.leave();
        } catch (leaveError) {
          if (__DEV__) {
            console.error('Error leaving Daily.co room:', leaveError);
          }
          // Continue with destroy even if leave fails
        }

        try {
          dailyCall.destroy();
        } catch (destroyError) {
          if (__DEV__) {
            console.error('Error destroying Daily.co call object:', destroyError);
          }
          // Continue with backend notification even if destroy fails
        }
      }

      // Notify backend conversation is ended
      if (conversationId) {
        try {
          await apiClient.post(`/api/v1/conversations/${conversationId}/end`);
        } catch (backendError) {
          if (__DEV__) {
            console.error('Error ending conversation on backend:', backendError);
          }
          // Continue with state reset even if backend call fails
        }
      }

      // Reset state
      set({
        conversationId: null,
        dailyCall: null,
        isConnected: false,
        isMicActive: false,
        isAISpeaking: false,
        error: null,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      set({ error: errorMessage });
      // Don't re-throw - cleanup should be best-effort
    }
  },

  /**
   * Action: Toggle microphone on/off
   *
   * Synchronous action that:
   * 1. Gets current dailyCall and isMicActive from state
   * 2. If dailyCall exists:
   *    - Calls setLocalAudio with inverted microphone state
   *    - Updates isMicActive in store
   * 3. If no dailyCall:
   *    - Action is no-op (silently ignored)
   *
   * This is a synchronous action and does not throw errors.
   */
  toggleMic: () => {
    const { dailyCall, isMicActive } = get();

    if (dailyCall) {
      try {
        // Toggle audio: if isMicActive is true, disable it (pass false), and vice versa
        dailyCall.setLocalAudio(!isMicActive);
        set({ isMicActive: !isMicActive });
      } catch (error) {
        if (__DEV__) {
          console.error('Error toggling microphone:', error);
        }
        // Silently fail - don't update state if SDK call fails
      }
    }
  },
}));

// Export type for component usage
export type { ConversationState };
