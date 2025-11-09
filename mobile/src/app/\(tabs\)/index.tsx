import React, { useCallback, useEffect, useRef } from 'react';
import {
  View,
  TouchableOpacity,
  Text,
  Alert,
  ActivityIndicator,
  StyleSheet,
  Animated,
  SafeAreaView,
  Platform,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { useConversationStore } from '@/stores/useConversationStore';
import {
  requestMicrophonePermission,
  checkMicrophonePermission,
} from '@/services/audio.service';

/**
 * Conversation Screen (Home Tab)
 *
 * Main UI for voice conversations. Presents a clean, minimal interface focused
 * on voice interaction with a central microphone button and status display.
 *
 * Features:
 * - Large microphone button as primary interaction element
 * - Dynamic status text reflecting connection state
 * - Microphone permission handling (check → request → start)
 * - Visual feedback and animations for state transitions
 * - Error handling with user-friendly alerts
 * - Cross-platform support (web PWA, Android, iOS)
 * - Responsive design for various screen sizes
 *
 * State Management:
 * - Uses Zustand store (useConversationStore) for conversation state
 * - Store provides: isConnected, isLoading, isAISpeaking, error state
 * - Store provides: startConversation(), endConversation() methods
 *
 * Permission Flow:
 * 1. User taps microphone button to start
 * 2. Check current permission status via checkMicrophonePermission()
 * 3. If not granted, request via requestMicrophonePermission()
 * 4. If granted, proceed to startConversation()
 * 5. If denied, show error alert and allow retry
 */
export default function ConversationScreen() {
  const {
    isConnected,
    isLoading,
    isAISpeaking,
    error,
    startConversation,
    endConversation,
  } = useConversationStore();

  // Debounce timer to prevent rapid button taps
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isHandlingRef = useRef(false);

  // Animated pulse for microphone icon
  const pulseAnim = useRef(new Animated.Value(1)).current;

  /**
   * Handle microphone button press
   * - If connected: end conversation
   * - If not connected: check permission, then start conversation
   */
  const handlePress = useCallback(async () => {
    // Debounce: prevent multiple rapid taps
    if (isHandlingRef.current) {
      return;
    }

    isHandlingRef.current = true;

    try {
      if (isConnected) {
        // End conversation
        await endConversation();
      } else {
        // Start conversation - with permission check
        try {
          // Step 1: Check if permission already granted
          let hasPermission = await checkMicrophonePermission();

          // Step 2: If not granted, request it
          if (!hasPermission) {
            hasPermission = await requestMicrophonePermission();
          }

          // Step 3: If still not granted, show error
          if (!hasPermission) {
            Alert.alert(
              'Microphone Required',
              'Please enable microphone access in app settings to use voice conversations.',
              [
                {
                  text: 'Cancel',
                  style: 'cancel',
                },
                {
                  text: 'Open Settings',
                  onPress: () => {
                    // This would normally open settings, but implementation
                    // varies by platform and store handling
                  },
                },
              ]
            );
            return;
          }

          // Step 4: Permission granted, start conversation
          await startConversation();
        } catch (err) {
          Alert.alert('Error', 'Failed to start conversation');
        }
      }
    } finally {
      // Clear debounce flag after a small delay
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
      debounceTimerRef.current = setTimeout(() => {
        isHandlingRef.current = false;
      }, 300);
    }
  }, [isConnected, startConversation, endConversation]);

  /**
   * Pulsing animation effect when connected
   * Creates a gentle pulsing motion on the microphone icon
   */
  useEffect(() => {
    if (isConnected && !isLoading) {
      // Start pulse animation
      const pulseSequence = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.15,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
        ])
      );

      pulseSequence.start();

      return () => {
        pulseSequence.stop();
        pulseAnim.setValue(1);
      };
    }
  }, [isConnected, isLoading, pulseAnim]);

  /**
   * Get dynamic status message based on connection state
   */
  const getStatusMessage = (): string => {
    if (isLoading) {
      return 'Connecting to AI...';
    }
    if (isAISpeaking) {
      return 'AI is speaking...';
    }
    if (isConnected) {
      return 'Connected - Speak now';
    }
    return 'Tap to start conversation';
  };

  /**
   * Get button styling based on connection state
   */
  const getButtonStyle = (): any[] => {
    const baseStyle = [styles.button];

    if (isLoading) {
      baseStyle.push(styles.buttonLoading);
    } else if (isConnected) {
      baseStyle.push(styles.buttonActive);
    } else {
      baseStyle.push(styles.buttonDefault);
    }

    return baseStyle;
  };

  /**
   * Get button content (icon or loading spinner)
   */
  const renderButtonContent = () => {
    if (isLoading) {
      return <ActivityIndicator size="large" color="#fff" />;
    }

    return (
      <Animated.View
        style={[
          styles.iconContainer,
          {
            transform: [{ scale: pulseAnim }],
          },
        ]}
      >
        <MaterialIcons
          name="mic"
          size={48}
          color={isConnected ? '#fff' : '#333'}
        />
      </Animated.View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Status Display */}
      <Text style={styles.status}>{getStatusMessage()}</Text>

      {/* Microphone Button */}
      <TouchableOpacity
        style={getButtonStyle()}
        onPress={handlePress}
        disabled={isLoading}
        activeOpacity={isLoading ? 1 : 0.7}
        accessible={true}
        accessibilityRole="button"
        accessibilityLabel={
          isConnected ? 'End conversation' : 'Start conversation'
        }
        accessibilityHint="Double tap to toggle conversation"
      >
        {renderButtonContent()}
      </TouchableOpacity>

      {/* Error Display */}
      {error && (
        <Text style={styles.error} accessible={true}>
          {error}
        </Text>
      )}

      {/* Button Label */}
      <Text style={styles.buttonLabel}>
        {isConnected ? 'End Conversation' : 'Start Conversation'}
      </Text>
    </SafeAreaView>
  );
}

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    paddingHorizontal: 20,
  },

  status: {
    fontSize: 18,
    marginBottom: 32,
    color: '#666666',
    textAlign: 'center',
    fontWeight: '500',
  },

  button: {
    width: 90,
    height: 90,
    borderRadius: 45,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 32,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 3.84,
      },
      android: {
        elevation: 5,
      },
    }),
  },

  buttonDefault: {
    backgroundColor: '#e0e0e0',
  },

  buttonActive: {
    backgroundColor: '#4CAF50',
  },

  buttonLoading: {
    backgroundColor: '#2196F3',
  },

  iconContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },

  buttonLabel: {
    fontSize: 14,
    color: '#999999',
    marginTop: 16,
    textAlign: 'center',
  },

  error: {
    color: '#f44336',
    marginTop: 16,
    fontSize: 14,
    textAlign: 'center',
    paddingHorizontal: 20,
  },
});
