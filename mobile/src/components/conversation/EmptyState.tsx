import React from 'react';
import { View, Text } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

export function EmptyState() {
  return (
    <View className="flex-1 items-center justify-center px-lg py-xxl">
      {/* Icon/Illustration */}
      <View className="w-24 h-24 rounded-full bg-primary/20 items-center justify-center mb-lg">
        <MaterialIcons name="mic" size={48} color="#d4af37" />
      </View>

      {/* Welcome Text */}
      <Text className="text-h1 font-bold text-text-primary text-center mb-sm">
        Welcome to Numerologist AI
      </Text>

      <Text className="text-body text-text-secondary text-center max-w-[280px] mb-xxl">
        Tap the button below to ask your first question about numerology
      </Text>

      {/* Optional: Mystical decorative element */}
      <View className="flex-row gap-sm">
        <View className="w-2 h-2 rounded-full bg-primary opacity-60" />
        <View className="w-2 h-2 rounded-full bg-secondary opacity-60" />
        <View className="w-2 h-2 rounded-full bg-accent opacity-60" />
      </View>
    </View>
  );
}
