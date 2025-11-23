import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ConversationCard } from '@/components/ConversationCard';
import { HistoryEmptyState } from '@/components/history/HistoryEmptyState';
import { fetchConversations, Conversation } from '@/services/api';

/**
 * History Screen
 *
 * Displays a paginated list of past conversations with pull-to-refresh
 * and infinite scroll functionality.
 */
export default function HistoryScreen() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  // Load conversations from API
  const loadConversations = useCallback(
    async (pageNum: number = 1, append: boolean = false) => {
      if (!append) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }
      setError(null);

      try {
        const response = await fetchConversations(pageNum, 20);

        if (append) {
          setConversations((prev) => [...prev, ...response.conversations]);
        } else {
          setConversations(response.conversations);
        }

        setHasMore(response.has_more);
        setPage(pageNum);
      } catch (err: any) {
        setError(err.message || 'Failed to load conversations');
        if (__DEV__) {
          console.error('Error loading conversations:', err);
        }
      } finally {
        setLoading(false);
        setRefreshing(false);
        setLoadingMore(false);
      }
    },
    []
  );

  // Initial load
  useEffect(() => {
    loadConversations(1, false);
  }, [loadConversations]);

  // Pull-to-refresh handler
  const onRefresh = useCallback(() => {
    setRefreshing(true);
    setPage(1);
    setHasMore(true);
    loadConversations(1, false);
  }, [loadConversations]);

  // Load more handler for pagination
  const onEndReached = useCallback(() => {
    if (hasMore && !loading && !loadingMore) {
      loadConversations(page + 1, true);
    }
  }, [hasMore, loading, loadingMore, page, loadConversations]);

  // Render loading state
  if (loading && conversations.length === 0) {
    return (
      <SafeAreaView className="flex-1 bg-dark">
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#d4af37" />
          <Text className="text-body text-text-secondary mt-md">
            Loading conversations...
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  // Render error state
  if (error && conversations.length === 0) {
    return (
      <SafeAreaView className="flex-1 bg-dark">
        <View className="flex-1 justify-center items-center px-lg">
          <Text className="text-h2 font-bold text-text-primary text-center mb-sm">
            Oops!
          </Text>
          <Text className="text-body text-text-secondary text-center mb-lg">
            {error}
          </Text>
          <Text
            className="text-body text-primary"
            onPress={() => loadConversations(1, false)}
          >
            Tap to retry
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  // Render footer for pagination
  const renderFooter = () => {
    if (!loadingMore) return null;

    return (
      <View className="py-md">
        <ActivityIndicator size="small" color="#d4af37" />
      </View>
    );
  };

  return (
    <SafeAreaView className="flex-1 bg-dark">
      {/* Header */}
      <View className="px-md py-sm border-b border-primary/20">
        <Text className="text-h1 font-bold text-text-primary">History</Text>
        {conversations.length > 0 && (
          <Text className="text-caption text-text-muted mt-xs">
            {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
          </Text>
        )}
      </View>

      {/* Conversation list */}
      <FlatList
        data={conversations}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ConversationCard conversation={item} />}
        contentContainerStyle={{
          paddingTop: 12,
          paddingBottom: 24,
          flexGrow: 1,
        }}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#d4af37"
            colors={['#d4af37']}
          />
        }
        onEndReached={onEndReached}
        onEndReachedThreshold={0.5}
        ListEmptyComponent={<HistoryEmptyState />}
        ListFooterComponent={renderFooter}
      />
    </SafeAreaView>
  );
}
