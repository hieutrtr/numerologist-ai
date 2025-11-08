import React, { useState, useRef, useEffect } from 'react';
import { View, ScrollView, Alert, Text, TouchableOpacity, Animated } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { RecordButton, MessageCard, LoadingWaveform, EmptyState } from '@/components/conversation';

interface Message {
  id: string;
  text: string;
  type: 'user' | 'ai';
  timestamp: string;
}

/**
 * Conversation/Home Screen
 *
 * Displays conversation history with a record button at the bottom.
 * Content-first layout: Shows message history, record button is always accessible.
 *
 * Features:
 * - Empty state for first-time users
 * - Message history with alternating user/AI messages
 * - Loading state with animated waveform
 * - Record button with pulsing animation
 * - Auto-scroll to latest messages
 */
export default function ConversationScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [headerCollapsed, setHeaderCollapsed] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);
  const headerHeight = useRef(new Animated.Value(1)).current;

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages, isLoading]);

  // Handle header collapse animation
  useEffect(() => {
    Animated.timing(headerHeight, {
      toValue: headerCollapsed ? 0 : 1,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [headerCollapsed, headerHeight]);

  // Get relative timestamp
  const getRelativeTime = (minutesAgo: number) => {
    if (minutesAgo === 0) return 'Just now';
    if (minutesAgo === 1) return '1 min ago';
    if (minutesAgo < 60) return `${minutesAgo} min ago`;
    const hoursAgo = Math.floor(minutesAgo / 60);
    if (hoursAgo === 1) return '1 hour ago';
    return `${hoursAgo} hours ago`;
  };

  // Handle record button press
  const handleRecordPress = async () => {
    if (isRecording || isLoading) return;

    try {
      setIsRecording(true);

      // Simulate recording delay (in real app, this would be actual voice recording)
      console.log('[MOCK] Starting voice recording...');
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Create mock user message
      const userMessage: Message = {
        id: `msg-${Date.now()}`,
        text: 'What is my life path number?', // Mock user input
        type: 'user',
        timestamp: getRelativeTime(0),
      };

      setMessages(prev => [...prev, userMessage]);
      setIsRecording(false);

      // Show loading state
      setIsLoading(true);
      console.log('[MOCK] Processing through numerology API...');
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Create mock AI response
      const aiMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        text: "Welcome! I'm your numerologist guide. Based on your birth information, your life path number reflects your natural talents and purpose. Let me calculate your complete numerology profile.",
        type: 'ai',
        timestamp: getRelativeTime(0),
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
      console.log('[MOCK] AI response received');
    } catch (error) {
      console.error('[ERROR] Recording failed:', error);
      Alert.alert('Error', 'Failed to record voice. Please try again.');
      setIsRecording(false);
      setIsLoading(false);
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <SafeAreaView className="flex-1 bg-dark">
      {/* Enhanced Header with Collapse */}
      <View className="border-b border-border/50">
        <TouchableOpacity
          className="px-lg py-md flex-row items-center justify-between"
          onPress={() => setHeaderCollapsed(!headerCollapsed)}
          activeOpacity={0.7}
        >
          <View className="flex-1">
            <View className="flex-row items-center gap-sm">
              <MaterialIcons name="auto-awesome" size={20} color="#d4af37" />
              <Text className="text-h2 font-bold text-text-primary">Numerology Guide</Text>
            </View>
            <Animated.View
              style={{
                maxHeight: headerHeight.interpolate({
                  inputRange: [0, 1],
                  outputRange: [0, 40],
                }),
                opacity: headerHeight,
                overflow: 'hidden',
              }}
            >
              <Text className="text-small text-text-secondary mt-xs">
                Try asking about your destiny number or life path
              </Text>
            </Animated.View>
          </View>
          <MaterialIcons
            name={headerCollapsed ? 'expand-more' : 'expand-less'}
            size={24}
            color="#9E9E9E"
          />
        </TouchableOpacity>
      </View>

      {/* Messages Area */}
      <ScrollView
        ref={scrollViewRef}
        className="flex-1 px-md py-md"
        contentContainerStyle={{ flexGrow: 1 }}
        scrollEventThrottle={16}
      >
        {isEmpty ? (
          // Empty state for new conversations
          <EmptyState />
        ) : (
          // Message history
          <>
            {messages.map((msg) => (
              <MessageCard
                key={msg.id}
                message={msg.text}
                type={msg.type}
                timestamp={msg.timestamp}
              />
            ))}

            {/* Loading state */}
            {isLoading && <LoadingWaveform />}
          </>
        )}
      </ScrollView>

      {/* Record Button (Fixed at Bottom) */}
      <View className="items-center py-lg pb-xxl bg-dark border-t border-border/50">
        <RecordButton
          onPress={handleRecordPress}
          isRecording={isRecording}
          disabled={isLoading}
        />
      </View>
    </SafeAreaView>
  );
}
