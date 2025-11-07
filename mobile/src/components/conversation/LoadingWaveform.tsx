import React from 'react';
import { View, Text, Animated, Easing } from 'react-native';

export function LoadingWaveform() {
  const bars = [
    React.useRef(new Animated.Value(10)).current,
    React.useRef(new Animated.Value(10)).current,
    React.useRef(new Animated.Value(10)).current,
    React.useRef(new Animated.Value(10)).current,
    React.useRef(new Animated.Value(10)).current,
  ];

  React.useEffect(() => {
    const animations = bars.map((bar, index) =>
      Animated.loop(
        Animated.sequence([
          Animated.timing(bar, {
            toValue: 40,
            duration: 600,
            delay: index * 100,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: false,
          }),
          Animated.timing(bar, {
            toValue: 10,
            duration: 600,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: false,
          }),
        ])
      )
    );

    Animated.parallel(animations).start();
  }, [bars]);

  return (
    <View className="items-center py-lg">
      <View className="flex-row items-end justify-center h-[60px] gap-xs mb-md">
        {bars.map((bar, index) => (
          <Animated.View
            key={index}
            className="w-[3px] rounded-sm bg-primary"
            style={{ height: bar }}
          />
        ))}
      </View>
      <Text className="text-small text-text-muted">
        AI is thinking...
      </Text>
    </View>
  );
}
