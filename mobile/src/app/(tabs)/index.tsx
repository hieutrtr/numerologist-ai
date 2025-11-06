import React from 'react';
import { View, Text, SafeAreaView, StyleSheet } from 'react-native';

/**
 * Conversation/Home Screen (Placeholder)
 *
 * This is a placeholder screen for the main conversation interface.
 * Full implementation will be in Epic 3: Voice Infrastructure & Basic Conversation
 */
export default function ConversationScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Conversation</Text>
        <Text style={styles.subtitle}>
          Voice conversation interface coming in Epic 3
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
});
