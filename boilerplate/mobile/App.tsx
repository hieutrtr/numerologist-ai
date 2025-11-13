/**
 * Voice Bot Mobile App - Entry Point
 *
 * Main application component with navigation setup.
 */

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Audio } from 'expo-av';

import ConversationScreen from './src/screens/ConversationScreen';

const Stack = createStackNavigator();

export default function App() {
  const [permissionsGranted, setPermissionsGranted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    requestPermissions();
  }, []);

  const requestPermissions = async () => {
    try {
      // Request audio recording permissions
      const { status } = await Audio.requestPermissionsAsync();

      if (status === 'granted') {
        console.log('Microphone permission granted');
        setPermissionsGranted(true);

        // Configure audio mode for voice recording
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: true,
          playsInSilentModeIOS: true,
        });
      } else {
        console.warn('Microphone permission denied');
        setPermissionsGranted(false);
      }
    } catch (error) {
      console.error('Error requesting permissions:', error);
      setPermissionsGranted(false);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  if (!permissionsGranted) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorTitle}>Permission Required</Text>
        <Text style={styles.errorText}>
          This app needs microphone access for voice conversations.
          Please enable it in your device settings.
        </Text>
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
        }}
      >
        <Stack.Screen name="Conversation" component={ConversationScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
    backgroundColor: '#F5F5F5',
  },
  loadingText: {
    fontSize: 16,
    color: '#666666',
    marginTop: 15,
  },
  errorTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#FF3B30',
    marginBottom: 15,
  },
  errorText: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 24,
  },
});
