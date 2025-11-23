# Story 5.4: Conversation Detail View

Status: ready-for-dev

## Story

As a user,
I want to see the full transcript of a past conversation,
so that I can review what the AI told me.

## Acceptance Criteria

1. Detail screen at `mobile/src/app/conversation/[id].tsx`
2. Shows conversation metadata (date, duration)
3. Displays full message history (user & AI messages)
4. Messages formatted as chat bubbles
5. User messages on right, AI messages on left
6. Scrollable if long conversation
7. Can navigate back to history list

## Tasks / Subtasks

- [ ] Task 1: Create Conversation Detail Screen (AC: #1-2)
  - [ ] Create `mobile/src/app/conversation/[id].tsx` dynamic route file
  - [ ] Extract `id` parameter using `useLocalSearchParams()` from Expo Router
  - [ ] Implement API call to GET `/api/v1/conversations/{id}` endpoint
  - [ ] Display conversation metadata (date, duration, main topic) in header
  - [ ] Format date using date-fns (consistent with Story 5.3 patterns)
  - [ ] Apply Celestial Gold design system styling

- [ ] Task 2: Implement Message Display (AC: #3-6)
  - [ ] Create `MessageBubble` component for displaying individual messages
  - [ ] Differentiate user messages (right-aligned, gold accent) from AI messages (left-aligned, purple accent)
  - [ ] Implement ScrollView or FlatList for message list (FlatList for performance with long conversations)
  - [ ] Add auto-scroll to latest message behavior
  - [ ] Handle loading state while fetching conversation
  - [ ] Handle error state if conversation not found or API fails

- [ ] Task 3: Navigation and Polish (AC: #7)
  - [ ] Add back button navigation to history screen
  - [ ] Ensure smooth navigation transitions
  - [ ] Test with various conversation lengths (0 messages, 1 message, 50+ messages)
  - [ ] Add empty state if conversation has no messages
  - [ ] Test message bubble wrapping for long text

## Dev Notes

### Architecture Patterns and Constraints

**From Architecture Document:**
- React Native with Expo framework [Source: docs/architecture.md#Frontend]
- TypeScript for type safety
- Expo Router for file-based routing with dynamic routes `[id].tsx`
- API client service at `mobile/src/services/api.ts` for backend calls
- SafeAreaView for device compatibility

**From UX Design Specification:**
- Use Celestial Gold design system colors [Source: docs/ux-design-specification.md#Design-Direction]
  - Primary: #d4af37 (Gold) for user messages
  - Secondary: #8b5cf6 (Purple) for AI messages
  - Background Dark: #0d0d1a
  - Background Light: #1a1a33 for message bubbles
  - Text Primary: #fef3c7
  - Text Muted: #a8960b

**API Integration:**
- Backend endpoint: GET `/api/v1/conversations/{id}` (from Story 5.2)
- Response format:
  ```json
  {
    "id": "uuid",
    "started_at": "ISO 8601",
    "ended_at": "ISO 8601 or null",
    "duration": "seconds or null",
    "main_topic": "string or null",
    "messages": [
      {
        "role": "user" | "assistant",
        "content": "string",
        "timestamp": "ISO 8601"
      }
    ]
  }
  ```
- Requires JWT authentication token in Authorization header

### Project Structure Notes

**File Locations:**
- Detail screen: `mobile/src/app/conversation/[id].tsx` (new dynamic route)
- Message bubble component: `mobile/src/components/conversation/MessageBubble.tsx` (new)
- API service: `mobile/src/services/api.ts` (extend existing)

**Naming Conventions:**
- Component files: PascalCase (MessageBubble.tsx)
- Functions/hooks: camelCase (fetchConversationDetail, useConversation)
- Screens: PascalCase default export (ConversationDetailScreen)

**Dependencies:**
- React Native ScrollView or FlatList for message scrolling
- Expo Router's `useLocalSearchParams()` for route parameters
- Expo Router's `router.back()` for navigation
- date-fns for date formatting (already installed in Story 5.3)
- Existing apiClient from services/api.ts

### Learnings from Previous Story

**From Story 5.3 (Frontend History Screen UI - Status: done)**

- **New Components Created**:
  - `ConversationCard` component at `mobile/src/components/ConversationCard.tsx` - use as reference for consistent styling patterns
  - `HistoryEmptyState` at `mobile/src/components/history/HistoryEmptyState.tsx` - follow same empty state pattern

- **API Service Pattern**: Extended `api.ts` with `fetchConversations()` function - follow same pattern for `fetchConversationDetail(id)`:
  ```typescript
  export const fetchConversationDetail = async (id: string) => {
    const response = await apiClient.get(`/api/v1/conversations/${id}`);
    return response.data;
  };
  ```

- **Date Formatting**: Story 5.3 uses date-fns with `format(date, 'MMM d, yyyy')` - maintain consistency

- **Design System Implementation**: Story 5.3 established patterns for:
  - Using NativeWind className syntax for styling
  - MaterialIcons for consistent iconography
  - SafeAreaView with `bg-dark` background
  - Card-based layout with `bg-background-light` and `border-primary/20`

- **State Management Pattern**: Implement loading, error, and data states similar to history screen

- **Navigation**: Use Expo Router's navigation hooks - `router.back()` for back navigation

[Source: docs/sprint-artifacts/5-3-frontend-history-screen-ui.md#Dev-Agent-Record]

### Implementation Guidance

**Dynamic Route Setup:**
```typescript
// File: mobile/src/app/conversation/[id].tsx
import { useLocalSearchParams, router } from 'expo-router';

export default function ConversationDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();

  // Fetch conversation details
  useEffect(() => {
    fetchConversationDetail(id);
  }, [id]);
}
```

**Message Bubble Component:**
```typescript
// File: mobile/src/components/conversation/MessageBubble.tsx
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
```

**API Service Extension:**
```typescript
// File: mobile/src/services/api.ts (extend existing)
export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ConversationDetail {
  id: string;
  started_at: string;
  ended_at: string | null;
  duration: number | null;
  main_topic: string | null;
  messages: ConversationMessage[];
}

export const fetchConversationDetail = async (
  id: string
): Promise<ConversationDetail> => {
  const response = await apiClient.get(`/api/v1/conversations/${id}`);
  return response.data;
};
```

### Testing Strategy

**Manual Testing:**
1. Navigate from history screen by tapping a conversation card
2. Verify conversation metadata displays correctly
3. Verify messages render in correct order (chronological)
4. Verify user messages are right-aligned with gold styling
5. Verify AI messages are left-aligned with purple styling
6. Test with short conversation (2-5 messages)
7. Test with long conversation (50+ messages, verify scrolling)
8. Test with conversation containing only user messages
9. Test with conversation containing only AI messages
10. Test back navigation returns to history screen

**Edge Cases:**
- Conversation not found (404 error)
- API error while loading
- No messages in conversation (empty state)
- Very long message text (word wrapping)
- Special characters or emojis in messages
- Conversation still active (ended_at is null)

**Performance:**
- Test with 100+ messages (FlatList virtualization)
- Ensure smooth scrolling
- Optimize re-renders (React.memo for MessageBubble)

### References

- Epic 5 Requirements: [Source: docs/epics.md#Story-5-4]
- Architecture Frontend: [Source: docs/architecture.md#Frontend]
- Backend API Endpoint: [Source: docs/sprint-artifacts/5-2-get-conversation-history-endpoint.md]
- Design System Colors: [Source: docs/ux-design-specification.md#Design-Direction-Summary]
- Navigation Setup: [Source: docs/epics.md#Story-2-9]
- Story 5.3 Patterns: [Source: docs/sprint-artifacts/5-3-frontend-history-screen-ui.md]

## Dev Agent Record

### Context Reference

- **Story Context**: [5-4-conversation-detail-view.context.xml](./5-4-conversation-detail-view.context.xml) - Generated 2025-11-23
  - Documentation artifacts (Epic 5 requirements, Architecture frontend, UX Design specification, Backend API from Story 5.2, Story 5.3 patterns)
  - Code artifacts (History screen reference, ConversationCard component, API client, EmptyState component)
  - Interfaces (REST endpoint, React Native components, API service functions)
  - Development constraints (React Native patterns, Expo Router dynamic routes, NativeWind styling, Celestial Gold design, authentication)
  - Test validation approach (Manual testing, edge cases, visual verification, performance testing)

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2025-11-23: Story created from Epic 5 requirements by create-story workflow
