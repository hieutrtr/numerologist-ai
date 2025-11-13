/**
 * Voice Visualizer Component
 *
 * Displays an animated visualization of voice activity.
 * Shows pulsing animation when active and bot presence.
 */

import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';

interface VoiceVisualizerProps {
  isActive: boolean;
  isBotSpeaking?: boolean;
}

export const VoiceVisualizer: React.FC<VoiceVisualizerProps> = ({
  isActive,
  isBotSpeaking = false,
}) => {
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (isActive) {
      // Start pulsing animation
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.3,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      // Reset animation
      pulseAnim.setValue(1);
    }
  }, [isActive, pulseAnim]);

  const backgroundColor = isBotSpeaking ? '#34C759' : '#007AFF';

  return (
    <View style={styles.container}>
      {/* Outer Ring */}
      <Animated.View
        style={[
          styles.outerRing,
          {
            transform: [{ scale: pulseAnim }],
            opacity: isActive ? 0.2 : 0,
            backgroundColor,
          },
        ]}
      />

      {/* Middle Ring */}
      <Animated.View
        style={[
          styles.middleRing,
          {
            transform: [{ scale: pulseAnim }],
            opacity: isActive ? 0.4 : 0,
            backgroundColor,
          },
        ]}
      />

      {/* Inner Circle */}
      <View
        style={[
          styles.innerCircle,
          {
            backgroundColor,
            opacity: isActive ? 1 : 0.3,
          },
        ]}
      >
        <View style={styles.icon}>
          {/* Microphone Icon (simplified) */}
          <View style={styles.micBody} />
          <View style={styles.micStand} />
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: 200,
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 40,
  },
  outerRing: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderRadius: 100,
  },
  middleRing: {
    position: 'absolute',
    width: 150,
    height: 150,
    borderRadius: 75,
  },
  innerCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  icon: {
    alignItems: 'center',
  },
  micBody: {
    width: 30,
    height: 40,
    backgroundColor: '#FFFFFF',
    borderRadius: 15,
  },
  micStand: {
    width: 2,
    height: 15,
    backgroundColor: '#FFFFFF',
    marginTop: 5,
  },
});

export default VoiceVisualizer;
