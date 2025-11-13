/**
 * Conversation Screen - Main Voice Conversation UI
 *
 * Displays the voice conversation interface with:
 * - Start/End conversation buttons
 * - Voice activity visualization
 * - Mute control
 * - Connection status
 * - Bot presence indicator
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import { useConversation } from '@/hooks/useConversation';
import VoiceVisualizer from '@/components/VoiceVisualizer';
import ConnectionStatus from '@/components/ConnectionStatus';

export const ConversationScreen: React.FC = () => {
  const {
    state,
    startConversation,
    endConversation,
    toggleMute,
    isMuted,
  } = useConversation();

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Voice Assistant</Text>
        <ConnectionStatus
          isConnected={state.isConnected}
          isBotPresent={state.isBotPresent}
        />
      </View>

      {/* Main Content */}
      <View style={styles.content}>
        {/* Voice Visualizer */}
        {state.isConnected && (
          <VoiceVisualizer
            isActive={state.isConnected && !isMuted}
            isBotSpeaking={state.isBotPresent}
          />
        )}

        {/* Status Messages */}
        {!state.isConnected && !state.isConnecting && (
          <View style={styles.instructions}>
            <Text style={styles.instructionsTitle}>Ready to Start</Text>
            <Text style={styles.instructionsText}>
              Tap the button below to begin your voice conversation with the AI assistant.
            </Text>
          </View>
        )}

        {state.isConnecting && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.loadingText}>Connecting...</Text>
          </View>
        )}

        {state.isConnected && !state.isBotPresent && (
          <View style={styles.waitingContainer}>
            <ActivityIndicator size="small" color="#007AFF" />
            <Text style={styles.waitingText}>Waiting for assistant to join...</Text>
          </View>
        )}

        {state.isConnected && state.isBotPresent && (
          <View style={styles.activeContainer}>
            <Text style={styles.activeTitle}>Conversation Active</Text>
            <Text style={styles.activeText}>
              Speak naturally - the assistant is listening
            </Text>
          </View>
        )}

        {/* Error Display */}
        {state.error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{state.error}</Text>
          </View>
        )}
      </View>

      {/* Controls */}
      <View style={styles.controls}>
        {!state.isConnected ? (
          <TouchableOpacity
            style={[
              styles.primaryButton,
              state.isConnecting && styles.buttonDisabled,
            ]}
            onPress={startConversation}
            disabled={state.isConnecting}
          >
            <Text style={styles.primaryButtonText}>
              {state.isConnecting ? 'Starting...' : 'Start Conversation'}
            </Text>
          </TouchableOpacity>
        ) : (
          <>
            {/* Mute Button */}
            <TouchableOpacity
              style={[styles.secondaryButton, isMuted && styles.mutedButton]}
              onPress={toggleMute}
            >
              <Text style={styles.secondaryButtonText}>
                {isMuted ? '🔇 Unmute' : '🔊 Mute'}
              </Text>
            </TouchableOpacity>

            {/* End Button */}
            <TouchableOpacity
              style={styles.dangerButton}
              onPress={endConversation}
            >
              <Text style={styles.dangerButtonText}>End Conversation</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 15,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000000',
    marginBottom: 10,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  instructions: {
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  instructionsTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#000000',
    marginBottom: 10,
  },
  instructionsText: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 24,
  },
  loadingContainer: {
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#007AFF',
    marginTop: 15,
  },
  waitingContainer: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  waitingText: {
    fontSize: 14,
    color: '#666666',
    marginTop: 10,
  },
  activeContainer: {
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  activeTitle: {
    fontSize: 22,
    fontWeight: '600',
    color: '#34C759',
    marginBottom: 8,
  },
  activeText: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
  },
  errorContainer: {
    backgroundColor: '#FFEBEE',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
  },
  errorText: {
    fontSize: 14,
    color: '#C62828',
    textAlign: 'center',
  },
  controls: {
    paddingHorizontal: 20,
    paddingBottom: 30,
    gap: 12,
  },
  primaryButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#007AFF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  primaryButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  secondaryButton: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#007AFF',
  },
  secondaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#007AFF',
  },
  mutedButton: {
    borderColor: '#FF3B30',
    backgroundColor: '#FFEBEE',
  },
  dangerButton: {
    backgroundColor: '#FF3B30',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  dangerButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
});

export default ConversationScreen;
