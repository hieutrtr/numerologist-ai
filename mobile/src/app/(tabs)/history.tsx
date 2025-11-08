import React from 'react';
import { View, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

/**
 * History Screen (Placeholder)
 *
 * This is a placeholder screen for conversation history.
 * Full implementation will be in Epic 5: Conversation History & Context Retention
 */
export default function HistoryScreen() {
  return (
    <SafeAreaView className="flex-1 bg-dark">
      <View className="flex-1 justify-center items-center p-lg">
        <Text className="text-h1 font-bold text-text-primary mb-md">History</Text>
        <Text className="text-body text-text-secondary text-center">
          Conversation history interface coming in Epic 5
        </Text>
      </View>
    </SafeAreaView>
  );
}
