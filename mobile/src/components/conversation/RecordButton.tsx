import React from 'react';
import { Pressable, Animated, Easing, View } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

interface RecordButtonProps {
  onPress: () => void;
  isRecording?: boolean;
  disabled?: boolean;
}

export function RecordButton({ onPress, isRecording = false, disabled = false }: RecordButtonProps) {
  const pulseAnim = React.useRef(new Animated.Value(1)).current;
  const wave1 = React.useRef(new Animated.Value(0)).current;
  const wave2 = React.useRef(new Animated.Value(0)).current;
  const wave3 = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    if (isRecording) {
      // Button pulsing animation when recording
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

      // Waveform rings animation
      const createWaveAnimation = (wave: Animated.Value, delay: number) => {
        return Animated.loop(
          Animated.sequence([
            Animated.delay(delay),
            Animated.parallel([
              Animated.timing(wave, {
                toValue: 1,
                duration: 1500,
                easing: Easing.out(Easing.ease),
                useNativeDriver: true,
              }),
            ]),
            Animated.timing(wave, {
              toValue: 0,
              duration: 0,
              useNativeDriver: true,
            }),
          ])
        );
      };

      createWaveAnimation(wave1, 0).start();
      createWaveAnimation(wave2, 500).start();
      createWaveAnimation(wave3, 1000).start();
    } else {
      pulseAnim.setValue(1);
      wave1.setValue(0);
      wave2.setValue(0);
      wave3.setValue(0);
    }
  }, [isRecording, pulseAnim, wave1, wave2, wave3]);

  const getWaveStyle = (wave: Animated.Value) => ({
    position: 'absolute' as const,
    width: 160,
    height: 160,
    borderRadius: 80,
    borderWidth: 2,
    borderColor: isRecording ? '#ef4444' : '#d4af37',
    opacity: wave.interpolate({
      inputRange: [0, 1],
      outputRange: [0.7, 0],
    }),
    transform: [
      {
        scale: wave.interpolate({
          inputRange: [0, 1],
          outputRange: [0.8, 1.4],
        }),
      },
    ],
  });

  return (
    <View className="items-center justify-center" style={{ width: 160, height: 160 }}>
      {/* Waveform rings - only visible when recording */}
      {isRecording && (
        <>
          <Animated.View style={getWaveStyle(wave1)} pointerEvents="none" />
          <Animated.View style={getWaveStyle(wave2)} pointerEvents="none" />
          <Animated.View style={getWaveStyle(wave3)} pointerEvents="none" />
        </>
      )}

      {/* Main button */}
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
    </View>
  );
}
