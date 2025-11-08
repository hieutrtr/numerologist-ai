import React from 'react';
import { View, Text, Animated } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

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
      className={`mb-xl px-sm ${isUser ? 'items-end' : 'items-start'}`}
      style={{ opacity: fadeAnim }}
    >
      {/* Wrapper for avatar + bubble on same line */}
      <View className={`flex-row items-center ${isUser ? 'flex-row-reverse' : ''}`}>
        {/* Avatar */}
        <View
          className={`
            w-10 h-10 rounded-full items-center justify-center
            ${isUser ? 'bg-chat-user ml-sm' : 'bg-chat-assistant mr-sm'}
          `}
          style={{
            shadowColor: isUser ? '#7C4DFF' : '#FFCA28',
            shadowOffset: { width: 0, height: 1 },
            shadowOpacity: 0.2,
            shadowRadius: 3,
            elevation: 2,
          }}
        >
          <MaterialIcons
            name={isUser ? 'person' : 'auto-awesome'}
            size={24}
            color={isUser ? '#ffffff' : '#1a1a33'}
          />
        </View>

        {/* Message Bubble */}
        <View
          className={`
            max-w-[50%] mt-md px-md py-md rounded-[20px] shadow-md
            ${isUser ? 'bg-chat-user' : 'bg-chat-assistant'}
          `}
          style={{
            shadowColor: isUser ? '#7C4DFF' : '#FFCA28',
            shadowOffset: { width: 0, height: 2 },
            shadowOpacity: 0.25,
            shadowRadius: 8,
            elevation: 4,
          }}
        >
          <Text className={`text-body leading-6 mb-xs ${isUser ? 'text-text-onPurple' : 'text-text-onGold'}`}>
            {message}
          </Text>
          <Text className={`text-tiny ${isUser ? 'text-white/70' : 'text-text-onGold/70'}`}>
            {timestamp}
          </Text>
        </View>
      </View>
    </Animated.View>
  );
}
