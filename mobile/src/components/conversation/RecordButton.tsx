import React from 'react';
import { Pressable, Animated, Easing } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

interface RecordButtonProps {
  onPress: () => void;
  isRecording?: boolean;
  disabled?: boolean;
}

export function RecordButton({ onPress, isRecording = false, disabled = false }: RecordButtonProps) {
  const pulseAnim = React.useRef(new Animated.Value(1)).current;

  React.useEffect(() => {
    if (isRecording) {
      // Pulsing animation when recording
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.1,
            duration: 600,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 600,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      pulseAnim.setValue(1);
    }
  }, [isRecording, pulseAnim]);

  return (
    <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
      <Pressable
        className={`
          w-32 h-32 rounded-full items-center justify-center
          ${isRecording ? 'bg-error shadow-[0_10px_20px_rgba(239,68,68,0.3)]' : 'bg-primary shadow-gold'}
          ${disabled ? 'bg-gray-700 opacity-50' : ''}
        `}
        onPress={onPress}
        disabled={disabled}
        accessibilityLabel="Record question"
        accessibilityRole="button"
        accessibilityState={{ disabled }}
      >
        <MaterialIcons
          name="mic"
          size={48}
          color={disabled ? '#666' : '#fff'}
        />
      </Pressable>
    </Animated.View>
  );
}
