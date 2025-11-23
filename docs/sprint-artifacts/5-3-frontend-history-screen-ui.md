# Story 5.3: Frontend History Screen UI

Status: drafted

## Story

As a user,
I want a history screen showing past conversations,
so that I can review what we talked about.

## Acceptance Criteria

1. History screen at `mobile/src/app/(tabs)/history.tsx`
2. Shows list of past conversations
3. Each item displays: date, duration, brief summary/topic
4. Tap to view full conversation details
5. Pull-to-refresh to reload list
6. Loading state while fetching
7. Empty state if no conversations yet
8. Pagination (load more on scroll)

## Tasks / Subtasks

- [ ] Task 1: Create History Screen Component (AC: #1-3)
  - [ ] Create `mobile/src/app/(tabs)/history.tsx` file
  - [ ] Set up React Native FlatList for conversation cards
  - [ ] Design conversation card component with date, duration, summary fields
  - [ ] Implement API call to GET /api/v1/conversations endpoint
  - [ ] Format timestamps and duration for display
  - [ ] Style cards following Celestial Gold design system

- [ ] Task 2: Implement Interactive Features (AC: #4-6)
  - [ ] Add onPress handler to navigate to conversation detail view
  - [ ] Implement pull-to-refresh using RefreshControl
  - [ ] Add loading spinner/skeleton during API fetch
  - [ ] Handle API errors with error state display
  - [ ] Test navigation to conversation detail screen

- [ ] Task 3: Handle Edge Cases (AC: #7-8)
  - [ ] Create empty state component ("No conversations yet")
  - [ ] Add empty state illustration/message
  - [ ] Implement infinite scroll pagination (load more on scroll end)
  - [ ] Handle pagination state (loading more, no more items)
  - [ ] Test with 0, 1, and 25+ conversations

## Dev Notes

### Architecture Patterns and Constraints

**From Architecture Document:**
- React Native with Expo framework [Source: docs/architecture.md#Frontend]
- TypeScript for type safety
- Expo Router for navigation (already configured in Story 2.9)
- API client service at `mobile/src/services/api.ts` for backend calls
- Bottom tab navigation already includes History tab from Story 2.9

**From UX Design Specification:**
- Use Celestial Gold design system colors [Source: docs/ux-design-specification.md#Design-Direction]
  - Primary: #d4af37 (Gold) for actions/highlights
  - Secondary: #8b5cf6 (Purple) for accents
  - Background Dark: #0d0d1a
  - Background Light: #1a1a33 for card surfaces
  - Text Primary: #fef3c7 (Pale gold)
  - Text Muted: #a8960b (Darker gold) for secondary info
- Card-based layout for conversation list
- Show: Date, first question, preview of insights, life path number if calculated
- Reverse chronological order (newest first) [Source: docs/ux-design-specification.md#Flow-3]

**API Integration:**
- Backend endpoint: GET /api/v1/conversations (from Story 5.2)
- Response format: `{ conversations: [], total: number, page: number, limit: number, has_more: boolean }`
- Each conversation: `{ id, started_at, ended_at, duration, main_topic }`
- Requires JWT authentication token in Authorization header

### Project Structure Notes

**File Locations:**
- History screen: `mobile/src/app/(tabs)/history.tsx` (tab already exists from Story 2.9)
- API service: `mobile/src/services/api.ts` (extend existing apiClient)
- Conversation card component: `mobile/src/components/ConversationCard.tsx` (new)
- Empty state component: `mobile/src/components/EmptyState.tsx` (new or reuse if exists)

**Naming Conventions:**
- Component files: PascalCase (ConversationCard.tsx)
- Functions/hooks: camelCase (fetchConversations, useConversations)
- Screens: PascalCase default export (HistoryScreen)

**Dependencies:**
- React Native FlatList for list rendering
- Expo Router's `useRouter()` for navigation
- RefreshControl from React Native for pull-to-refresh
- AsyncStorage or secure storage for auth token
- Date formatting library (date-fns or similar) for timestamp display

### Learnings from Previous Stories

**From Story 5.2 (Backend Endpoints):**
- API endpoint available: GET /api/v1/conversations
- Supports pagination: ?page=1&limit=20
- Returns conversations ordered by most recent first (started_at DESC)
- Each conversation has: id (UUID string), started_at (ISO string), ended_at (ISO string or null), duration (seconds or null), main_topic (string or null)
- main_topic field currently returns null (not yet implemented)
- Authentication required: Must include JWT token in Authorization header
- Returns 403 if not authenticated, 422 for invalid pagination params

**From Story 2.9 (Tab Navigation):**
- Bottom tab navigation already configured with History tab
- Tab bar navigation uses Expo Router file-based routing
- History tab located at `mobile/src/app/(tabs)/history.tsx`
- Tab icons and styling already defined in layout file

**From Story 3.4 (Conversation Flow):**
- User authentication flow already implemented
- JWT tokens stored in secure storage
- API client configured with interceptors for auth headers

### Implementation Guidance

**Fetching Conversations:**
```typescript
// File: mobile/src/services/api.ts (extend existing)
export const fetchConversations = async (page = 1, limit = 20) => {
  const response = await apiClient.get('/api/v1/conversations', {
    params: { page, limit }
  });
  return response.data;
};
```

**History Screen Structure:**
```typescript
// File: mobile/src/app/(tabs)/history.tsx
import { FlatList, RefreshControl } from 'react-native';
import { ConversationCard } from '@/components/ConversationCard';

export default function HistoryScreen() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const loadConversations = async (pageNum = 1, append = false) => {
    // Fetch and set conversations
  };

  const onRefresh = () => {
    setPage(1);
    loadConversations(1, false);
  };

  const loadMore = () => {
    if (hasMore && !loading) {
      loadConversations(page + 1, true);
    }
  };

  return (
    <FlatList
      data={conversations}
      renderItem={({ item }) => <ConversationCard conversation={item} />}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      onEndReached={loadMore}
      onEndReachedThreshold={0.5}
      ListEmptyComponent={<EmptyState />}
    />
  );
}
```

**Conversation Card Component:**
```typescript
// File: mobile/src/components/ConversationCard.tsx
import { Pressable, View, Text } from 'react-native';
import { useRouter } from 'expo-router';

export function ConversationCard({ conversation }) {
  const router = useRouter();

  const handlePress = () => {
    router.push(`/conversation/${conversation.id}`);
  };

  return (
    <Pressable onPress={handlePress}>
      <View style={styles.card}>
        <Text style={styles.date}>{formatDate(conversation.started_at)}</Text>
        <Text style={styles.duration}>{formatDuration(conversation.duration)}</Text>
        <Text style={styles.topic}>{conversation.main_topic || 'New conversation'}</Text>
      </View>
    </Pressable>
  );
}
```

**Date Formatting:**
```typescript
import { format } from 'date-fns';

const formatDate = (isoString: string) => {
  const date = new Date(isoString);
  return format(date, 'MMM d, yyyy h:mm a'); // "Nov 23, 2025 2:30 PM"
};

const formatDuration = (seconds: number | null) => {
  if (!seconds) return 'In progress';
  const minutes = Math.floor(seconds / 60);
  return `${minutes} min`;
};
```

### Testing Strategy

**Manual Testing:**
1. Test with empty history (new user)
2. Test with 1 conversation
3. Test with 25+ conversations (pagination)
4. Test pull-to-refresh
5. Test navigation to detail view
6. Test loading states
7. Test error states (API failure)
8. Test pagination (scroll to end, load more)

**Edge Cases:**
- No internet connection
- API returns error
- Very long conversation duration
- Conversation without ended_at (still active)
- main_topic is null (not yet implemented)

**Performance:**
- Test with 100+ conversations in list
- Ensure smooth scrolling
- Optimize re-renders (React.memo for ConversationCard)
- Use FlatList virtualization for large lists

### References

- Epic 5 Requirements: [Source: docs/epics.md#Story-5-3]
- UX Design Flow 3: [Source: docs/ux-design-specification.md#Flow-3-Reviewing-Past-Readings]
- Architecture Frontend: [Source: docs/architecture.md#Frontend]
- Backend API Endpoint: [Source: docs/sprint-artifacts/5-2-get-conversation-history-endpoint.md]
- Design System Colors: [Source: docs/ux-design-specification.md#Design-Direction-Summary]
- Navigation Setup: [Source: docs/epics.md#Story-2-9]

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2025-11-23: Story created from Epic 5 requirements by create-story workflow
