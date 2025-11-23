import { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  ActivityIndicator,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';
import { format } from 'date-fns';
import { fetchConversationDetail, ConversationDetail } from '@/services/api';
import { MessageBubble } from '@/components/conversation/MessageBubble';

export default function ConversationDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConversation();
  }, [id]);

  const loadConversation = async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);
      const data = await fetchConversationDetail(id);
      setConversation(data);
    } catch (err: any) {
      console.error('Error loading conversation:', err);
      setError(err.message || 'Failed to load conversation');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }
      return format(date, 'MMM d, yyyy');
    } catch (error) {
      return 'Invalid date';
    }
  };

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'In progress';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  if (loading) {
    return (
      <SafeAreaView className="flex-1 bg-dark">
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#d4af37" />
          <Text className="text-text-muted mt-md">Loading conversation...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error || !conversation) {
    return (
      <SafeAreaView className="flex-1 bg-dark">
        <View className="flex-1 justify-center items-center px-lg">
          <MaterialIcons name="error-outline" size={64} color="#a8960b" />
          <Text className="text-heading3 text-text-primary mt-md mb-sm">
            {error || 'Conversation not found'}
          </Text>
          <TouchableOpacity
            onPress={() => router.back()}
            className="mt-lg px-xl py-md bg-primary/20 border border-primary/40 rounded-lg"
          >
            <Text className="text-body text-primary font-medium">Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const hasMessages = conversation.messages && conversation.messages.length > 0;

  return (
    <SafeAreaView className="flex-1 bg-dark">
      {/* Header */}
      <View className="px-lg py-md border-b border-background-light">
        <View className="flex-row items-center mb-sm">
          <TouchableOpacity
            onPress={() => router.back()}
            className="mr-md p-sm"
            hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          >
            <MaterialIcons name="arrow-back" size={24} color="#d4af37" />
          </TouchableOpacity>
          <Text className="text-heading3 text-text-primary flex-1">
            Conversation Details
          </Text>
        </View>

        {/* Metadata */}
        <View className="ml-xl">
          <Text className="text-body text-text-muted">
            {formatDate(conversation.started_at)}
          </Text>
          <Text className="text-caption text-text-muted mt-xs">
            Duration: {formatDuration(conversation.duration)}
          </Text>
          {conversation.main_topic && (
            <Text className="text-caption text-text-muted mt-xs">
              Topic: {conversation.main_topic}
            </Text>
          )}
        </View>
      </View>

      {/* Messages */}
      {hasMessages ? (
        <FlatList
          data={conversation.messages}
          keyExtractor={(item, index) => `${item.timestamp}-${index}`}
          renderItem={({ item }) => (
            <MessageBubble
              role={item.role}
              content={item.content}
              timestamp={item.timestamp}
            />
          )}
          contentContainerStyle={{ padding: 16 }}
          showsVerticalScrollIndicator={false}
        />
      ) : (
        <View className="flex-1 justify-center items-center px-lg">
          <MaterialIcons name="chat-bubble-outline" size={64} color="#a8960b" />
          <Text className="text-heading3 text-text-primary mt-md mb-sm">
            No messages yet
          </Text>
          <Text className="text-body text-text-muted text-center">
            This conversation doesn't have any messages.
          </Text>
        </View>
      )}
    </SafeAreaView>
  );
}
