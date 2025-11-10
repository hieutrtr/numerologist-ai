/**
 * Daily.co Service - React Native Voice Integration
 *
 * Manages Daily.co WebRTC connection lifecycle for voice conversations.
 * Handles call object creation, room joining, event setup, and cleanup.
 *
 * Architecture:
 * - Bridges React Native frontend with Daily.co infrastructure
 * - Event-driven: All Daily.co events trigger store updates
 * - Store (useConversationStore) is single source of truth for UI
 * - All errors mapped to user-friendly messages
 *
 * Integration Points:
 * - useConversationStore: Receives call object and manages state
 * - Story 3.4 Backend: Provides room_url and daily_token
 * - Story 3.6 Audio Service: Microphone permissions prerequisite
 */

import { Platform } from 'react-native';

/**
 * Platform detection helper
 * Determines if we're in a native environment or web
 */
const isNativeEnvironment = (): boolean => {
  try {
    return Platform.OS !== 'web';
  } catch {
    return false;
  }
};

/**
 * Type definitions for Daily.co integration
 */

export interface DailyCallObject {
  join: (opts: { url: string; token?: string }) => Promise<any>;
  leave: () => Promise<void>;
  destroy: () => void;
  on: (event: string, callback: (...args: any[]) => void) => void;
  off: (event: string, callback: (...args: any[]) => void) => void;
  getParticipants: () => Record<string, any>;
  getParticipantCount: () => number;
  // Audio control methods - same in both web (daily-js) and React Native (react-native-daily-js)
  setLocalAudio: (enabled: boolean) => DailyCallObject; // Returns 'this' for chaining
  setLocalVideo: (enabled: boolean) => DailyCallObject; // Returns 'this' for chaining
  localAudio: () => boolean | null; // Returns current audio state or null if not in call
  localVideo: () => boolean | null; // Returns current video state or null if not in call
}

export interface RoomCredentials {
  roomUrl: string;
  token: string;
}

export interface AudioConfig {
  audioInputEnabled?: boolean;
  audioOutputEnabled?: boolean;
  audioSource?: string;
  noiseSuppression?: boolean;
  echoCancellation?: boolean;
}

export interface ParticipantInfo {
  id: string;
  name?: string;
  isLocal?: boolean;
  audioState?: {
    blocked?: boolean;
    muted?: boolean;
  };
  videoState?: {
    blocked?: boolean;
    muted?: boolean;
  };
}

export interface DailyServiceCallbacks {
  onConnected?: () => void;
  onDisconnected?: () => void;
  onError?: (error: string) => void;
  onParticipantJoined?: (participant: ParticipantInfo) => void;
  onParticipantLeft?: (participantId: string) => void;
  onNetworkQuality?: (quality: 'good' | 'ok' | 'poor') => void;
}

/**
 * Initialize Daily.co call object with proper configuration
 *
 * @returns Promise<DailyCallObject> - Configured call object
 * @throws Error if initialization fails
 */
export async function initializeCall(): Promise<DailyCallObject> {
  try {
    let DailyIframe;

    // Use appropriate SDK based on platform
    if (isNativeEnvironment()) {
      // React Native: Use react-native-daily-js
      DailyIframe = require('@daily-co/react-native-daily-js').default ||
                    require('@daily-co/react-native-daily-js');
    } else {
      // Web/Expo Web: Use daily-js (web SDK)
      DailyIframe = require('@daily-co/daily-js').default ||
                    require('@daily-co/daily-js');
    }

    const call = await DailyIframe.createCallObject({
      videoSource: false, // No video for voice-first app
      audioSource: true,  // Enable audio input
      // Note: audioOutput is not a valid property for createCallObject()
      // Audio output is automatically configured when joining a room
      receiveSettings: {
        // CRITICAL: Subscribe to all audio tracks to hear remote participants (bot)
        audio: {
          subscribeToAll: true,  // Subscribe to all audio tracks
        },
        screenAudio: {
          subscribeToAll: true,  // Subscribe to screen share audio if any
        },
        screenVideo: {
          subscribeToAll: false, // Don't subscribe to screen video
        },
        video: {
          subscribeToAll: false, // Don't subscribe to video tracks
        },
      },
    });
    console.log('DailyIframe:', DailyIframe);
    console.log('Daily call object:', call);

    if (!call) {
      throw new Error('Failed to create Daily call object');
    }

    if (__DEV__) {
      console.log('[Daily] Call object initialized on', isNativeEnvironment() ? 'native' : 'web');
    }

    return call;
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    if (__DEV__) {
      console.error('[Daily] Failed to initialize call object:', errorMsg);
    }
    throw new Error(`Daily.co initialization failed: ${errorMsg}`);
  }
}

/**
 * Configure audio settings for the call
 *
 * Handles platform-specific audio routing (Android speaker vs receiver)
 * and audio constraints to prevent clipping and ensure quality.
 *
 * @param call - Daily call object
 * @param config - Audio configuration options
 */
export async function configureAudio(
  call: DailyCallObject,
  config: AudioConfig = {}
): Promise<void> {
  try {
    const {
      audioInputEnabled = true,
      audioOutputEnabled = true,
      noiseSuppression = true,
      echoCancellation = true,
    } = config;

    // Set audio input (microphone) using Daily.co SDK method
    // Note: Daily.co SDKs use setLocalAudio() not setAudioInputEnabled()
    // This method is the same across both web (daily-js) and React Native (react-native-daily-js)
    if (audioInputEnabled !== undefined) {
      call.setLocalAudio(audioInputEnabled);
    }

    // Note: Daily.co doesn't have a separate setAudioOutputEnabled() method.
    // Audio output (speaker) is controlled by the system/platform level.
    // In React Native, the native layer handles speaker routing via setNativeInCallAudioMode()
    // For web, speaker output is handled by browser audio output configuration.
    if (audioOutputEnabled !== undefined && __DEV__) {
      console.log('[Daily] Audio output is system-managed, not directly controllable via SDK');
    }

    // Platform-specific audio routing
    if (Platform.OS === 'android') {
      // Android: Prefer speaker over receiver for better voice quality
      // This is typically handled by the native layer in @daily-co/react-native-daily-js
      if (__DEV__) {
        console.log('[Daily] Audio configured for Android (speaker preferred)');
      }
    } else if (Platform.OS === 'ios') {
      // iOS: Use speaker for calls (not receiver)
      if (__DEV__) {
        console.log('[Daily] Audio configured for iOS (speaker)');
      }
    } else if (Platform.OS === 'web') {
      // Web: Browser handles speaker configuration via system audio settings
      if (__DEV__) {
        console.log('[Daily] Audio configured for Web (browser-managed)');
      }
    }

    if (__DEV__) {
      console.log('[Daily] Audio configured:', {
        audioInputEnabled,
        audioOutputEnabled: 'system-managed',
        noiseSuppression,
        echoCancellation,
      });
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    if (__DEV__) {
      console.error('[Daily] Audio configuration failed:', errorMsg);
    }
    throw new Error(`Audio configuration failed: ${errorMsg}`);
  }
}

/**
 * Join a Daily.co room with credentials
 *
 * Establishes WebRTC connection to the room and configures audio.
 * Must be called after initializeCall().
 *
 * @param call - Daily call object
 * @param credentials - Room URL and optional token
 * @param audioConfig - Optional audio configuration
 * @returns Promise<void>
 * @throws Error if joining fails (invalid URL, permission issue, etc.)
 */
export async function joinRoom(
  call: DailyCallObject,
  credentials: RoomCredentials,
  audioConfig?: AudioConfig
): Promise<void> {
  try {
    const { roomUrl, token } = credentials;

    // Validate credentials
    if (!roomUrl) {
      throw new Error('Room URL is required');
    }

    if (!roomUrl.startsWith('http')) {
      throw new Error('Invalid room URL format');
    }

    if (__DEV__) {
      console.log('[Daily] Joining room:', roomUrl.split('/').pop());
    }

    // Configure audio before joining
    if (audioConfig) {
      await configureAudio(call, audioConfig);
    } else {
      // Default configuration
      await configureAudio(call);
    }

    // Join the room
    await call.join({
      url: roomUrl,
      ...(token && { token }),
    });

    if (__DEV__) {
      console.log('[Daily] Successfully joined room');
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);

    if (__DEV__) {
      console.error('[Daily] Failed to join room:', errorMsg);
    }

    // Map errors to user-friendly messages
    let userMessage = 'Failed to join call';
    if (errorMsg.includes('Invalid') || errorMsg.includes('URL')) {
      userMessage = 'Invalid room URL or token';
    } else if (errorMsg.includes('expired') || errorMsg.includes('not found')) {
      userMessage = 'Room expired or no longer available';
    } else if (errorMsg.includes('permission') || errorMsg.includes('access')) {
      userMessage = 'Permission denied - check audio settings';
    } else if (errorMsg.includes('network') || errorMsg.includes('timeout')) {
      userMessage = 'Network error - check your connection';
    }

    throw new Error(userMessage);
  }
}

/**
 * Setup event listeners for Daily.co call events
 *
 * Wires Daily.co events to store updates. All events update store state,
 * which triggers UI re-renders via Zustand.
 *
 * @param call - Daily call object
 * @param callbacks - Object with callback functions for each event
 */
export function setupCallListeners(
  call: DailyCallObject,
  callbacks: DailyServiceCallbacks
): () => void {
  // Track listener functions so we can remove them later
  const listeners: Array<{ event: string; handler: (...args: any[]) => void }> = [];

  try {
    // Connection events
    if (callbacks.onConnected) {
      const handler = () => {
        if (__DEV__) {
          console.log('[Daily] Connected to room');
        }
        callbacks.onConnected?.();
      };
      call.on('joined-meeting', handler);
      listeners.push({ event: 'joined-meeting', handler });
    }

    if (callbacks.onDisconnected) {
      const handler = () => {
        if (__DEV__) {
          console.log('[Daily] Disconnected from room');
        }
        callbacks.onDisconnected?.();
      };
      call.on('left-meeting', handler);
      listeners.push({ event: 'left-meeting', handler });
    }

    // Error event
    if (callbacks.onError) {
      const handler = (error: any) => {
        const errorMsg = error?.message || String(error);
        if (__DEV__) {
          console.error('[Daily] Error event:', errorMsg);
        }
        callbacks.onError?.(errorMsg);
      };
      call.on('error', handler);
      listeners.push({ event: 'error', handler });
    }

    // Participant events
    if (callbacks.onParticipantJoined) {
      const handler = (event: any) => {
        const participant = event.participant;
        if (__DEV__) {
          console.log('[Daily] Participant joined:', participant?.id);
        }
        if (participant) {
          callbacks.onParticipantJoined?.({
            id: participant.session_id || participant.id,
            name: participant.name,
            isLocal: participant.local,
            audioState: {
              muted: participant.audio === false,
              blocked: participant.audioBlock === true,
            },
            videoState: {
              muted: participant.video === false,
              blocked: participant.videoBlock === true,
            },
          });

          // CRITICAL: Create audio element for remote participant (web only)
          if (!participant.local && participant.audioTrack && Platform.OS === 'web') {
            const participantId = participant.session_id || participant.id;
            manageAudioElement(participantId, participant.audioTrack, 'create');
          }
        }
      };
      call.on('participant-joined', handler);
      listeners.push({ event: 'participant-joined', handler });
    }

    if (callbacks.onParticipantLeft) {
      const handler = (event: any) => {
        const participantId = event.participant?.session_id || event.participant?.id;
        if (__DEV__) {
          console.log('[Daily] Participant left:', participantId);
        }
        if (participantId) {
          callbacks.onParticipantLeft?.(participantId);

          // Clean up audio element for web
          if (Platform.OS === 'web') {
            manageAudioElement(participantId, null, 'remove');
          }
        }
      };
      call.on('participant-left', handler);
      listeners.push({ event: 'participant-left', handler });
    }

    // CRITICAL: Handle participant-updated for audio track changes
    const participantUpdatedHandler = (event: any) => {
      const participant = event.participant;
      if (!participant || participant.local) {
        return; // Skip local participant
      }

      const participantId = participant.session_id || participant.id;

      if (__DEV__) {
        console.log('[Daily] Participant updated:', {
          id: participantId,
          audio: participant.audio,
          hasAudioTrack: !!participant.audioTrack,
        });
      }

      // Handle audio track changes for web
      if (Platform.OS === 'web') {
        if (participant.audioTrack && participant.audio) {
          // Audio track available and unmuted
          manageAudioElement(participantId, participant.audioTrack, 'create');
        } else {
          // Audio track removed or muted
          manageAudioElement(participantId, null, 'remove');
        }
      }
    };
    call.on('participant-updated', participantUpdatedHandler);
    listeners.push({ event: 'participant-updated', handler: participantUpdatedHandler });

    // Network quality
    if (callbacks.onNetworkQuality) {
      const handler = (event: any) => {
        const quality = event?.quality || 'ok';
        if (__DEV__) {
          console.log('[Daily] Network quality:', quality);
        }
        callbacks.onNetworkQuality?.(quality);
      };
      call.on('network-quality-change', handler);
      listeners.push({ event: 'network-quality-change', handler });
    }

    // Track events for audio playback (CRITICAL for hearing remote participants)
    // Listen for when remote audio tracks start
    const trackStartedHandler = (event: any) => {
      if (__DEV__) {
        console.log('[Daily] Track started:', {
          participant: event.participant?.session_id,
          track: event.track?.kind,
          type: event.type,
        });
      }
      // Track started events indicate remote audio is available
      if (event.track?.kind === 'audio' && !event.participant?.local) {
        console.log('[Daily] Remote audio track started - you should now hear the bot');

        // CRITICAL: Create audio element when track starts (web only)
        if (Platform.OS === 'web' && event.track) {
          const participantId = event.participant?.session_id || event.participant?.id;
          if (participantId) {
            manageAudioElement(participantId, event.track, 'create');
          }
        }
      }
    };
    call.on('track-started', trackStartedHandler);
    listeners.push({ event: 'track-started', handler: trackStartedHandler });

    // Listen for track updates
    const trackUpdatedHandler = (event: any) => {
      if (__DEV__) {
        console.log('[Daily] Track updated:', {
          participant: event.participant?.session_id,
          track: event.track?.kind,
          state: event.track?.state,
        });
      }
    };
    call.on('track-updated', trackUpdatedHandler);
    listeners.push({ event: 'track-updated', handler: trackUpdatedHandler });

    // Listen for when tracks stop
    const trackStoppedHandler = (event: any) => {
      if (__DEV__) {
        console.log('[Daily] Track stopped:', {
          participant: event.participant?.session_id,
          track: event.track?.kind,
        });
      }
    };
    call.on('track-stopped', trackStoppedHandler);
    listeners.push({ event: 'track-stopped', handler: trackStoppedHandler });

    if (__DEV__) {
      console.log('[Daily] Event listeners setup:', listeners.length, 'listeners');
    }

    // Return cleanup function
    return () => {
      listeners.forEach(({ event, handler }) => {
        call.off(event, handler);
      });
      if (__DEV__) {
        console.log('[Daily] Event listeners cleaned up');
      }
    };
  } catch (error) {
    if (__DEV__) {
      console.error('[Daily] Failed to setup listeners:', error);
    }
    // Return empty cleanup function if setup fails
    return () => {};
  }
}

/**
 * Teardown and cleanup Daily.co call object
 *
 * Removes all event listeners and closes the connection.
 * Should be called when conversation ends.
 *
 * @param call - Daily call object
 * @param cleanupListeners - Optional cleanup function from setupCallListeners
 */
export async function teardownCall(
  call: DailyCallObject,
  cleanupListeners?: () => void
): Promise<void> {
  try {
    // Remove event listeners
    if (cleanupListeners) {
      cleanupListeners();
    }

    // Leave the room
    if (call) {
      await call.leave();
      if (__DEV__) {
        console.log('[Daily] Left room');
      }
    }

    // Destroy the call object
    if (call) {
      call.destroy();
      if (__DEV__) {
        console.log('[Daily] Call object destroyed');
      }
    }
  } catch (error) {
    if (__DEV__) {
      console.error('[Daily] Error during teardown:', error);
    }
    // Don't throw - cleanup should be forgiving
    // Try to at least destroy the call object
    try {
      call?.destroy();
    } catch {
      // Ignore
    }
  }
}

/**
 * Get current participant list
 *
 * Returns all participants currently in the room including the user.
 *
 * @param call - Daily call object
 * @returns Array of participant info objects
 */
export function getParticipants(call: DailyCallObject): ParticipantInfo[] {
  try {
    const participants = call.getParticipants();
    if (!participants) {
      return [];
    }

    return Object.values(participants).map((p: any) => ({
      id: p.session_id || p.id,
      name: p.name,
      isLocal: p.local,
      audioState: {
        muted: p.audio === false,
        blocked: p.audioBlock === true,
      },
      videoState: {
        muted: p.video === false,
        blocked: p.videoBlock === true,
      },
    }));
  } catch (error) {
    if (__DEV__) {
      console.error('[Daily] Error getting participants:', error);
    }
    return [];
  }
}

/**
 * Check if call object is connected
 *
 * @param call - Daily call object
 * @returns boolean - True if connected to a room
 */
export function isConnected(call: DailyCallObject): boolean {
  try {
    // A simple heuristic: if we have participants including local, we're connected
    const participants = call.getParticipants();
    return participants && Object.keys(participants).length > 0;
  } catch {
    return false;
  }
}

/**
 * Manage audio elements for web playback
 *
 * CRITICAL: Daily.co doesn't automatically create audio elements for remote participants.
 * We must manually create HTML audio elements and attach the MediaStreamTrack.
 *
 * @param participantId - Unique identifier for the participant
 * @param audioTrack - MediaStreamTrack for audio
 * @param action - 'create' to add audio, 'remove' to cleanup
 */
export function manageAudioElement(
  participantId: string,
  audioTrack?: MediaStreamTrack | null,
  action: 'create' | 'remove' = 'create'
): void {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return; // Not in browser environment
  }

  const audioElementId = `daily-audio-${participantId}`;
  const existingElement = document.getElementById(audioElementId) as HTMLAudioElement;

  if (action === 'remove' || !audioTrack) {
    // Remove existing audio element
    if (existingElement) {
      existingElement.pause();
      existingElement.srcObject = null;
      existingElement.remove();
      if (__DEV__) {
        console.log(`[Daily] Removed audio element for participant ${participantId}`);
      }
    }
    return;
  }

  // Create or update audio element
  let audioElement = existingElement;

  if (!audioElement) {
    // Create new audio element
    audioElement = document.createElement('audio');
    audioElement.id = audioElementId;
    audioElement.autoplay = true; // Important for WebRTC
    audioElement.playsInline = true; // For mobile browsers

    // Hide the element (audio only, no visual)
    audioElement.style.display = 'none';

    // Append to document body
    document.body.appendChild(audioElement);

    if (__DEV__) {
      console.log(`[Daily] Created audio element for participant ${participantId}`);
    }
  }

  // Create MediaStream from the audio track
  const stream = new MediaStream([audioTrack]);
  audioElement.srcObject = stream;

  // Attempt to play
  audioElement.play().then(() => {
    console.log(`✅ [Daily] Audio playing for participant ${participantId}`);
  }).catch((error) => {
    console.error(`❌ [Daily] Failed to play audio for ${participantId}:`, error);

    // Common autoplay policy issue - might need user interaction
    if (error.name === 'NotAllowedError') {
      console.warn('[Daily] Browser autoplay policy blocked audio. User interaction required.');
    }
  });
}

/**
 * Debug audio state for all participants
 *
 * Helps diagnose audio playback issues by logging detailed audio state
 * for all participants including track information.
 *
 * @param call - Daily call object
 */
export function debugAudioState(call: DailyCallObject): void {
  try {
    const participants = call.getParticipants();

    console.log('=== Daily Audio Debug ===');
    console.log('Total participants:', Object.keys(participants).length);

    Object.entries(participants).forEach(([id, participant]: [string, any]) => {
      console.log(`\nParticipant: ${id}`);
      console.log('  Name:', participant.name || 'Unknown');
      console.log('  Local:', participant.local);
      console.log('  Audio State:', {
        audio: participant.audio,
        audioTrack: participant.audioTrack ? 'Present' : 'Missing',
        tracks: participant.tracks,
      });

      // Check for audio tracks
      if (participant.tracks) {
        Object.entries(participant.tracks).forEach(([trackId, track]: [string, any]) => {
          if (track.kind === 'audio') {
            console.log(`  Audio Track ${trackId}:`, {
              state: track.state,
              subscribed: track.subscribed,
              blocked: track.blocked,
              off: track.off,
              playable: track.playable,
            });
          }
        });
      }
    });

    console.log('=== End Audio Debug ===');
  } catch (error) {
    console.error('[Daily] Audio debug error:', error);
  }
}

export default {
  initializeCall,
  configureAudio,
  joinRoom,
  setupCallListeners,
  teardownCall,
  getParticipants,
  isConnected,
  debugAudioState,
  manageAudioElement,
};
