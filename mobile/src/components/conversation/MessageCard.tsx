import React from 'react';
import { View, Text, Animated } from 'react-native';

interface MessageCardProps {
  message: string;
  type: 'user' | 'ai';
  timestamp: string;
}

export function MessageCard({ message, type, timestamp }: MessageCardProps) {
  const fadeAnim = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
  }, [fadeAnim]);

  const isUser = type === 'user';

  return (
    <Animated.View
      className={`mb-md px-md ${isUser ? 'items-end' : 'items-start'}`}
      style={{ opacity: fadeAnim }}
    >
      <View
        className={`
          max-w-[80%] p-md rounded-xl border-l-4
          ${isUser
            ? 'bg-elevated border-secondary'
            : 'bg-card border-primary'
          }
        `}
      >
        <Text className="text-body text-text-primary mb-xs">
          {message}
        </Text>
        <Text className="text-tiny text-text-muted">
          {timestamp}
        </Text>
      </View>
    </Animated.View>
  );
}
