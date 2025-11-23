import React from 'react';
import { Pressable, View, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';
import { format } from 'date-fns';

interface ConversationCardProps {
  conversation: {
    id: string;
    started_at: string;
    ended_at: string | null;
    duration: number | null;
    main_topic: string | null;
  };
}

export function ConversationCard({ conversation }: ConversationCardProps) {
  const router = useRouter();

  const handlePress = () => {
    router.push(`/conversation/${conversation.id}`);
  };

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return format(date, 'h:mm a');
    } else if (diffInHours < 48) {
      return 'Yesterday';
    } else {
      return format(date, 'MMM d, yyyy');
    }
  };

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'In progress';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 1) return '< 1 min';
    if (minutes < 60) return `${minutes} min`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  return (
    <Pressable
      onPress={handlePress}
      className="mx-md mb-sm active:opacity-80"
      style={({ pressed }) => [{ opacity: pressed ? 0.8 : 1 }]}
    >
      <View className="bg-background-light rounded-lg p-md border border-primary/20">
        {/* Header with date and duration */}
        <View className="flex-row justify-between items-center mb-sm">
          <View className="flex-row items-center">
            <MaterialIcons name="access-time" size={16} color="#a8960b" />
            <Text className="text-caption text-text-muted ml-xs">
              {formatDate(conversation.started_at)}
            </Text>
          </View>
          <View className="flex-row items-center">
            <MaterialIcons name="timer" size={16} color="#a8960b" />
            <Text className="text-caption text-text-muted ml-xs">
              {formatDuration(conversation.duration)}
            </Text>
          </View>
        </View>

        {/* Main topic or placeholder */}
        <Text className="text-body text-text-primary mb-xs" numberOfLines={2}>
          {conversation.main_topic || 'New conversation'}
        </Text>

        {/* Status indicator */}
        {!conversation.ended_at && (
          <View className="flex-row items-center mt-sm">
            <View className="w-2 h-2 rounded-full bg-secondary mr-xs" />
            <Text className="text-caption text-secondary">Active</Text>
          </View>
        )}

        {/* Navigate indicator */}
        <View className="absolute right-md top-1/2 -translate-y-1/2">
          <MaterialIcons name="chevron-right" size={24} color="#d4af37" />
        </View>
      </View>
    </Pressable>
  );
}
