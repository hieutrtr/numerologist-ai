/**
 * useConversation Hook - Voice Conversation Management
 *
 * Manages the complete lifecycle of a voice conversation:
 * 1. Start conversation (create room)
 * 2. Join Daily.co room
 * 3. Handle audio events
 * 4. End conversation and cleanup
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import Daily, { DailyCall, DailyEventObjectParticipant, DailyEventObjectTrack } from '@daily-co/react-native-daily-js';
import { apiClient } from '@/services/api';

export interface ConversationState {
  isConnecting: boolean;
  isConnected: boolean;
  isBotPresent: boolean;
  error: string | null;
  conversationId: string | null;
  roomUrl: string | null;
}

export interface ConversationHook {
  state: ConversationState;
  startConversation: () => Promise<void>;
  endConversation: () => Promise<void>;
  toggleMute: () => void;
  isMuted: boolean;
}

/**
 * Custom hook for managing voice conversations
 *
 * @returns ConversationHook with state and control methods
 *
 * @example
 * ```tsx
 * function ConversationScreen() {
 *   const { state, startConversation, endConversation, toggleMute, isMuted } = useConversation();
 *
 *   return (
 *     <View>
 *       <Button onPress={startConversation} disabled={state.isConnecting}>
 *         Start Conversation
 *       </Button>
 *       {state.isConnected && (
 *         <Button onPress={endConversation}>End</Button>
 *       )}
 *     </View>
 *   );
 * }
 * ```
 */
export const useConversation = (): ConversationHook => {
  const [state, setState] = useState<ConversationState>({
    isConnecting: false,
    isConnected: false,
    isBotPresent: false,
    error: null,
    conversationId: null,
    roomUrl: null,
  });

  const [isMuted, setIsMuted] = useState(false);
  const callObjectRef = useRef<DailyCall | null>(null);

  /**
   * Cleanup function to destroy Daily call object
   */
  const cleanup = useCallback(() => {
    if (callObjectRef.current) {
      callObjectRef.current.destroy();
      callObjectRef.current = null;
    }
  }, []);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  /**
   * Handle participant joined event
   */
  const handleParticipantJoined = useCallback((event: DailyEventObjectParticipant) => {
    console.log('Participant joined:', event.participant);

    // Check if bot joined (bot typically has specific username or is the first non-local participant)
    if (!event.participant.local) {
      setState((prev) => ({ ...prev, isBotPresent: true }));
      console.log('Bot has joined the conversation');
    }
  }, []);

  /**
   * Handle participant left event
   */
  const handleParticipantLeft = useCallback((event: DailyEventObjectParticipant) => {
    console.log('Participant left:', event.participant);

    if (!event.participant.local) {
      setState((prev) => ({ ...prev, isBotPresent: false }));
      console.log('Bot has left the conversation');
    }
  }, []);

  /**
   * Handle track started event (audio/video)
   */
  const handleTrackStarted = useCallback((event: DailyEventObjectTrack) => {
    console.log('Track started:', event.track);
  }, []);

  /**
   * Handle track stopped event
   */
  const handleTrackStopped = useCallback((event: DailyEventObjectTrack) => {
    console.log('Track stopped:', event.track);
  }, []);

  /**
   * Handle call errors
   */
  const handleError = useCallback((error: any) => {
    console.error('Daily.co error:', error);
    setState((prev) => ({
      ...prev,
      error: error.errorMsg || 'Connection error',
      isConnecting: false,
      isConnected: false,
    }));
  }, []);

  /**
   * Start a new voice conversation
   */
  const startConversation = useCallback(async () => {
    try {
      setState((prev) => ({
        ...prev,
        isConnecting: true,
        error: null,
      }));

      // 1. Call backend to create conversation and Daily room
      console.log('Starting conversation...');
      const response = await apiClient.startConversation();

      console.log('Conversation created:', response.conversation_id);
      console.log('Room URL:', response.daily_room_url);

      setState((prev) => ({
        ...prev,
        conversationId: response.conversation_id,
        roomUrl: response.daily_room_url,
      }));

      // 2. Create Daily.co call object
      const callObject = Daily.createCallObject({
        audioSource: true,   // Enable microphone
        videoSource: false,  // Disable camera (audio only)
      });

      callObjectRef.current = callObject;

      // 3. Register event handlers
      callObject
        .on('participant-joined', handleParticipantJoined)
        .on('participant-left', handleParticipantLeft)
        .on('track-started', handleTrackStarted)
        .on('track-stopped', handleTrackStopped)
        .on('error', handleError);

      // 4. Join the room
      console.log('Joining Daily.co room...');
      await callObject.join({
        url: response.daily_room_url,
        token: response.daily_token,
      });

      console.log('Successfully joined room');

      setState((prev) => ({
        ...prev,
        isConnecting: false,
        isConnected: true,
      }));
    } catch (error: any) {
      console.error('Failed to start conversation:', error);
      setState((prev) => ({
        ...prev,
        isConnecting: false,
        isConnected: false,
        error: error.detail || error.message || 'Failed to start conversation',
      }));
      cleanup();
    }
  }, [handleParticipantJoined, handleParticipantLeft, handleTrackStarted, handleTrackStopped, handleError, cleanup]);

  /**
   * End the active conversation
   */
  const endConversation = useCallback(async () => {
    try {
      console.log('Ending conversation...');

      // 1. Leave Daily.co room
      if (callObjectRef.current) {
        await callObjectRef.current.leave();
      }

      // 2. Notify backend
      if (state.conversationId) {
        await apiClient.endConversation(state.conversationId);
        console.log('Conversation ended:', state.conversationId);
      }

      // 3. Cleanup
      cleanup();

      // 4. Reset state
      setState({
        isConnecting: false,
        isConnected: false,
        isBotPresent: false,
        error: null,
        conversationId: null,
        roomUrl: null,
      });

      setIsMuted(false);

      console.log('Conversation cleanup complete');
    } catch (error: any) {
      console.error('Error ending conversation:', error);
      // Still cleanup even if backend call fails
      cleanup();
      setState((prev) => ({
        ...prev,
        isConnected: false,
        error: 'Failed to end conversation cleanly',
      }));
    }
  }, [state.conversationId, cleanup]);

  /**
   * Toggle microphone mute/unmute
   */
  const toggleMute = useCallback(() => {
    if (callObjectRef.current) {
      const newMuteState = !isMuted;
      callObjectRef.current.setLocalAudio(!newMuteState);
      setIsMuted(newMuteState);
      console.log('Microphone', newMuteState ? 'muted' : 'unmuted');
    }
  }, [isMuted]);

  return {
    state,
    startConversation,
    endConversation,
    toggleMute,
    isMuted,
  };
};

export default useConversation;
