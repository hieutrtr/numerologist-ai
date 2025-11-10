import { create } from 'zustand';
import { apiClient } from '../services/api';
import * as dailyService from '../services/daily.service';

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
  debugAudio: () => void; // Debug audio state for troubleshooting
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
    let cleanupListeners: (() => void) | null = null;

    try {
      // Step 1: Call backend to create conversation and get Daily.co credentials
      if (__DEV__) {
        console.log('[Store] Starting conversation - calling backend');
      }

      const response = await apiClient.post<ConversationStartResponse>(
        '/api/v1/conversations/start'
      );

      const { conversation_id, daily_room_url, daily_token } = response.data;

      if (!conversation_id || !daily_room_url || !daily_token) {
        throw new Error('Backend did not return required conversation details');
      }

      if (__DEV__) {
        console.log('[Store] Backend returned credentials for conversation:', conversation_id);
      }

      // Step 2: Initialize Daily.co call object
      const callObject = await dailyService.initializeCall();

      // Step 3: Setup event listeners to update store on Daily.co events
      cleanupListeners = dailyService.setupCallListeners(callObject, {
        onConnected: () => {
          set({ isConnected: true, error: null });
          if (__DEV__) {
            console.log('[Store] Update: connected');
          }
        },
        onDisconnected: () => {
          set({ isConnected: false });
          if (__DEV__) {
            console.log('[Store] Update: disconnected');
          }
        },
        onError: (errorMsg: string) => {
          // Map error to user-friendly message if needed
          let userMessage = errorMsg;
          if (errorMsg.includes('permission')) {
            userMessage = 'Microphone permission denied';
          } else if (errorMsg.includes('network')) {
            userMessage = 'Network error - check your connection';
          }
          set({ error: userMessage });
          if (__DEV__) {
            console.log('[Store] Error:', userMessage);
          }
        },
        onParticipantJoined: (participant) => {
          if (__DEV__) {
            console.log('[Store] Participant joined:', participant.id, participant.isLocal ? '(local)' : '(bot)');
          }
          // Store can track participants if needed for future features
        },
        onParticipantLeft: (participantId) => {
          if (__DEV__) {
            console.log('[Store] Participant left:', participantId);
          }
        },
        onNetworkQuality: (quality) => {
          if (__DEV__) {
            console.log('[Store] Network quality:', quality);
          }
          // Could update network quality indicator in future
        },
      });

      // Step 4: Join the Daily.co room with credentials
      if (__DEV__) {
        console.log('[Store] Joining Daily.co room...');
      }

      await dailyService.joinRoom(callObject, {
        roomUrl: daily_room_url,
        token: daily_token,
      });

      // Step 5: Update store state with connection details
      set({
        conversationId: conversation_id,
        dailyCall: callObject,
        isConnected: true,
        isMicActive: true,
        error: null,
      });

      if (__DEV__) {
        console.log('[Store] Conversation started successfully');
      }
    } catch (error) {
      // Clean up listeners if they were setup but connection failed
      if (cleanupListeners) {
        cleanupListeners();
      }

      const errorMessage = error instanceof Error ? error.message : String(error);

      // Map technical errors to user-friendly messages
      let userMessage = errorMessage;
      if (errorMessage.includes('Backend did not return')) {
        userMessage = 'Server error - please try again';
      } else if (errorMessage.includes('room')) {
        userMessage = 'Failed to join room - room may be expired';
      } else if (errorMessage.includes('audio') || errorMessage.includes('permission')) {
        userMessage = 'Microphone access required to start conversation';
      } else if (errorMessage.includes('network')) {
        userMessage = 'Network error - check your internet connection';
      }

      set({ error: userMessage });

      if (__DEV__) {
        console.error('[Store] Failed to start conversation:', errorMessage);
      }

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
      if (__DEV__) {
        console.log('[Store] Ending conversation');
      }

      // Step 1: Clean up Daily.co call using daily.service
      if (dailyCall) {
        try {
          await dailyService.teardownCall(dailyCall);
          if (__DEV__) {
            console.log('[Store] Daily.co call cleaned up');
          }
        } catch (teardownError) {
          if (__DEV__) {
            console.error('[Store] Error during Daily.co cleanup:', teardownError);
          }
          // Continue with backend notification even if cleanup fails
        }
      }

      // Step 2: Notify backend conversation is ended
      if (conversationId) {
        try {
          await apiClient.post(`/api/v1/conversations/${conversationId}/end`);
          if (__DEV__) {
            console.log('[Store] Backend notified of conversation end');
          }
        } catch (backendError) {
          if (__DEV__) {
            console.error('[Store] Error ending conversation on backend:', backendError);
          }
          // Continue with state reset even if backend call fails
        }
      }

      // Step 3: Reset state
      set({
        conversationId: null,
        dailyCall: null,
        isConnected: false,
        isMicActive: false,
        isAISpeaking: false,
        error: null,
      });

      if (__DEV__) {
        console.log('[Store] Conversation ended and state reset');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      if (__DEV__) {
        console.error('[Store] Error during conversation end:', errorMessage);
      }
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

  /**
   * Debug audio state for troubleshooting playback issues
   * Call this from browser console: useConversationStore.getState().debugAudio()
   */
  debugAudio: () => {
    const { dailyCall } = get();

    if (dailyCall) {
      console.log('🔊 Debugging Audio State...');
      dailyService.debugAudioState(dailyCall);

      // Also log current store state
      const state = get();
      console.log('Store State:', {
        conversationId: state.conversationId,
        isConnected: state.isConnected,
        isMicActive: state.isMicActive,
        isAISpeaking: state.isAISpeaking,
        error: state.error,
      });
    } else {
      console.log('⚠️ No active Daily call to debug');
    }
  },
}));

// Export type for component usage
export type { ConversationState };

// Expose store to window for debugging (only in development)
if (typeof window !== 'undefined' && __DEV__) {
  (window as any).conversationStore = useConversationStore;
}
