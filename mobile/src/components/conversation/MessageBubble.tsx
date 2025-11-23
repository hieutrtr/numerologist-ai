import { View, Text } from 'react-native';
import { format } from 'date-fns';

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export function MessageBubble({ role, content, timestamp }: MessageBubbleProps) {
  const isUser = role === 'user';

  return (
    <View className={`flex-row mb-sm ${isUser ? 'justify-end' : 'justify-start'}`}>
      <View
        className={`max-w-[80%] p-md rounded-lg ${
          isUser
            ? 'bg-primary/20 border border-primary/40'
            : 'bg-background-light border border-secondary/40'
        }`}
      >
        <Text className="text-body text-text-primary mb-xs">{content}</Text>
        <Text className="text-caption text-text-muted text-right">
          {format(new Date(timestamp), 'h:mm a')}
        </Text>
      </View>
    </View>
  );
}
