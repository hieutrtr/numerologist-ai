import React, { useCallback, useRef, useEffect } from 'react';
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
  Dimensions,
} from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useConversationStore } from '../../stores/useConversationStore';
import {
  requestMicrophonePermission,
  checkMicrophonePermission,
} from '../../services/audio.service';

/**
 * Conversation Screen Component
 *
 * Main interface for voice conversations with the numerology AI.
 * Features a large microphone button that displays conversation state and handles
 * permission management, conversation lifecycle, and visual feedback.
 *
 * **State Management:**
 * - All state managed by useConversationStore (Zustand)
 * - Component is a pure view of store state
 * - No local state except for UI animations
 *
 * **Permission Flow:**
 * 1. User taps microphone button
 * 2. Check if microphone permission already granted
 * 3. If not, request permission (shows native dialog)
 * 4. If granted, call store.startConversation()
 * 5. Store handles Daily.co connection and bot communication
 *
 * **States:**
 * - Not connected: "Start Conversation" button, neutral styling
 * - Connecting: Loading spinner, disabled state
 * - Connected: "End Conversation" button, pulsing animation
 * - AI Speaking: Different color/animation indicator
 */
export default function ConversationScreen() {
  // Get state and actions from conversation store
  const {
    isConnected,
    isAISpeaking,
    error: storeError,
    startConversation,
    endConversation,
  } = useConversationStore();

  // Animation values for pulsing microphone when connected
  const pulseAnim = useRef(new Animated.Value(1)).current;

  // Track if currently processing permission/start to prevent rapid taps
  const isProcessingRef = useRef(false);

  // Debounce timeout ref
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Start pulsing animation when connected
  useEffect(() => {
    if (isConnected) {
      // Pulse animation: scale 1 -> 1.2 -> 1, repeat
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.2,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      // Reset animation value when disconnected
      pulseAnim.setValue(1);
    }
  }, [isConnected, pulseAnim]);

  /**
   * Handle microphone button press with permission checking
   * and debouncing to prevent rapid fires
   */
  const handlePress = useCallback(async () => {
    // Prevent rapid taps
    if (isProcessingRef.current) {
      return;
    }

    // Clear any existing debounce timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    // If connected, end the conversation
    if (isConnected) {
      isProcessingRef.current = true;
      try {
        await endConversation();
      } catch (err) {
        Alert.alert(
          'Error',
          'Failed to end conversation. Please try again.'
        );
      } finally {
        isProcessingRef.current = false;
      }
      return;
    }

    // If not connected, start conversation with permission check
    isProcessingRef.current = true;

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
            { text: 'OK', onPress: () => {} },
            {
              text: 'Settings',
              onPress: () => {
                // In a real app, this would open app settings
                // For now, just acknowledge
              },
            },
          ]
        );
        return;
      }

      // Step 4: Permission granted, start conversation
      await startConversation();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      Alert.alert(
        'Connection Error',
        errorMsg || 'Failed to start conversation. Please try again.'
      );
    } finally {
      // Use debounce to prevent rapid re-taps
      debounceTimeoutRef.current = setTimeout(() => {
        isProcessingRef.current = false;
      }, 500);
    }
  }, [isConnected, startConversation, endConversation]);

  /**
   * Generate status message based on connection state
   */
  const getStatusMessage = () => {
    if (storeError) {
      return `Error: ${storeError}`;
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
  const getButtonStyle = () => {
    const baseStyle = [styles.button];

    if (isAISpeaking) {
      return [...baseStyle, styles.buttonAISpeaking];
    }

    if (isConnected) {
      return [...baseStyle, styles.buttonActive];
    }

    return [...baseStyle, styles.buttonDefault];
  };

  /**
   * Get button text based on connection state
   */
  const getButtonText = () => {
    return isConnected ? 'End' : 'Start';
  };

  /**
   * Get microphone icon based on state
   */
  const renderMicrophoneIcon = () => {
    const iconColor = isConnected ? '#fff' : '#333';
    const iconSize = 40;

    // Loading spinner
    if (storeError === null && isConnected === false && isAISpeaking === false) {
      // Not loading, just render static icon
      return (
        <MaterialCommunityIcons
          name="microphone"
          size={iconSize}
          color={iconColor}
        />
      );
    }

    // Connected state - pulsing animation
    if (isConnected && !isAISpeaking) {
      return (
        <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
          <MaterialCommunityIcons
            name="microphone"
            size={iconSize}
            color={iconColor}
          />
        </Animated.View>
      );
    }

    // AI speaking state
    if (isAISpeaking) {
      return (
        <MaterialCommunityIcons
          name="microphone"
          size={iconSize}
          color={iconColor}
        />
      );
    }

    // Default state
    return (
      <MaterialCommunityIcons
        name="microphone"
        size={iconSize}
        color={iconColor}
      />
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Status Text Display */}
      <Text style={styles.status}>{getStatusMessage()}</Text>

      {/* Microphone Button */}
      <TouchableOpacity
        style={getButtonStyle()}
        onPress={handlePress}
        disabled={isProcessingRef.current}
        activeOpacity={0.85}
        accessibilityRole="button"
        accessibilityLabel={isConnected ? 'End conversation' : 'Start conversation'}
      >
        {renderMicrophoneIcon()}
      </TouchableOpacity>

      {/* Button Label */}
      <Text style={styles.buttonLabel}>{getButtonText()} Conversation</Text>

      {/* Loading Indicator (below button) */}
      {storeError === null && isConnected === false && !isAISpeaking ? null : (
        <View style={styles.stateIndicator}>
          {isAISpeaking && (
            <View style={styles.speakingIndicator}>
              <MaterialCommunityIcons
                name="waveform"
                size={20}
                color="#FF9800"
              />
              <Text style={styles.speakingText}>Processing...</Text>
            </View>
          )}
        </View>
      )}
    </SafeAreaView>
  );
}

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

// Responsive sizing
const buttonSize = Math.min(screenWidth * 0.35, 100);
const minTouchTarget = 48; // Material Design minimum
const actualButtonSize = Math.max(buttonSize, minTouchTarget);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    paddingHorizontal: 20,
  },

  status: {
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
    marginBottom: 48,
    textAlign: 'center',
    minHeight: 24,
  },

  button: {
    width: actualButtonSize,
    height: actualButtonSize,
    borderRadius: actualButtonSize / 2,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 32,
    elevation: 4, // Android shadow
    shadowColor: '#000', // iOS shadow
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3,
  },

  buttonDefault: {
    backgroundColor: '#e0e0e0',
  },

  buttonActive: {
    backgroundColor: '#4CAF50',
  },

  buttonAISpeaking: {
    backgroundColor: '#FF9800',
  },

  buttonLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginTop: 8,
    textAlign: 'center',
  },

  stateIndicator: {
    marginTop: 32,
    alignItems: 'center',
  },

  speakingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFF3E0',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FFE0B2',
  },

  speakingText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#FF9800',
  },
});
