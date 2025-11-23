import React from 'react';
import { View, Text } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

export function HistoryEmptyState() {
  return (
    <View className="flex-1 items-center justify-center px-lg py-xxl">
      {/* Icon */}
      <View className="w-24 h-24 rounded-full bg-primary/20 items-center justify-center mb-lg">
        <MaterialIcons name="history" size={48} color="#d4af37" />
      </View>

      {/* Message */}
      <Text className="text-h2 font-bold text-text-primary text-center mb-sm">
        No Conversations Yet
      </Text>

      <Text className="text-body text-text-secondary text-center max-w-[280px] mb-xxl">
        Your conversation history will appear here after you start your first reading
      </Text>

      {/* Decorative element */}
      <View className="flex-row gap-sm">
        <View className="w-2 h-2 rounded-full bg-primary opacity-60" />
        <View className="w-2 h-2 rounded-full bg-secondary opacity-60" />
        <View className="w-2 h-2 rounded-full bg-accent opacity-60" />
      </View>
    </View>
  );
}
