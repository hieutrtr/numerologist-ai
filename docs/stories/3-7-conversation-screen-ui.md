# Story 3.7: Conversation Screen UI

**Epic:** Epic 3 - Voice Infrastructure & Basic Conversation
**Story ID:** 3-7-conversation-screen-ui
**Status:** drafted
**Created:** 2025-11-10
**Context Reference:** docs/stories/3-7-conversation-screen-ui.context.xml

---

## User Story

**As a** user,
**I want** a conversation screen with microphone button,
**So that** I can start and control voice conversations.

---

## Acceptance Criteria

### AC1: Conversation Screen Component
- [ ] Conversation screen created in `mobile/src/app/(tabs)/index.tsx` (home tab)
- [ ] Screen is the main tab in the navigation layout
- [ ] Screen has clean, minimal design focused on voice interaction
- [ ] Works on both web (PWA) and mobile (Android/iOS)
- [ ] Proper styling using React Native styles (cross-platform compatibility)

### AC2: Microphone Button - Main Control
- [ ] Large central microphone button occupies prominent screen position
- [ ] Button is TouchableOpacity component for proper mobile interaction
- [ ] Button text/label shows action: "Start Conversation" (when disconnected) or "End Conversation" (when connected)
- [ ] Button responds to single tap (no double-tap needed)
- [ ] Proper button sizing for mobile accessibility (minimum 48dp touch target)
- [ ] Button is centered vertically and horizontally on screen

### AC3: Button State Management
- [ ] Button integrates with `useConversationStore` state
- [ ] Button reflects current connection state:
  - **Not connected**: Text "Start Conversation", neutral styling
  - **Connecting**: Shows loading spinner, disabled state
  - **Connected**: Text "End Conversation", pulsing mic icon, active styling
  - **AI Speaking**: Visual indicator different from idle (color change or animation)
- [ ] State changes triggered by store state updates (isConnected, isLoading, isAISpeaking)
- [ ] Visual feedback on state transitions (smooth animations)

### AC4: Permission Handling
- [ ] On start button tap, first checks microphone permission
- [ ] Calls `requestMicrophonePermission()` from audio.service if not already granted
- [ ] If permission denied, shows Alert dialog with clear message
- [ ] Alert message: "Microphone Required - Please enable microphone access in app settings"
- [ ] Permission check happens BEFORE attempting to start conversation
- [ ] If permission granted, proceeds to start conversation

### AC5: Conversation Control Flow
- [ ] Tap start button: Request permission → Call `startConversation()` from store
- [ ] Tap end button: Call `endConversation()` from store
- [ ] Start flow: Permission → Store.startConversation() → UI updates to "connected"
- [ ] End flow: Store.endConversation() → UI updates to "not connected"
- [ ] Proper error handling if start/end operations fail
- [ ] Error alerts show user-friendly messages

### AC6: Connection Status Display
- [ ] Status text displayed above or below microphone button
- [ ] Text updates based on connection state:
  - Not connected: "Tap to start conversation"
  - Connecting: "Connecting to AI..."
  - Connected: "Connected - Speak now"
  - AI Speaking: "AI is speaking..." or similar
- [ ] Text is readable and properly styled
- [ ] Text updates reactively based on store state

### AC7: Visual Feedback & Animations
- [ ] Microphone icon inside button
- [ ] Icon styling reflects connection state (color, animation, opacity)
- [ ] When connected: Pulsing animation on microphone icon
- [ ] Button styling changes visually between states (color scheme)
- [ ] Animations are smooth and performance-optimized
- [ ] Loading spinner when connecting (with proper styling)
- [ ] No animation delays or janky transitions

### AC8: Integration with Store
- [ ] Screen correctly imports and uses `useConversationStore` hook
- [ ] Store provides: `isConnected`, `isLoading`, `isAISpeaking` state
- [ ] Screen calls: `startConversation()`, `endConversation()` store methods
- [ ] Store errors surfaced to user via error alerts
- [ ] No direct API calls from screen (all through store)
- [ ] Clean separation of concerns: store handles logic, screen handles UI

### AC9: Error Handling & Edge Cases
- [ ] Handles permission denial gracefully (shows alert, button remains clickable)
- [ ] Handles start conversation failure (shows error alert, button resets)
- [ ] Handles end conversation failure (shows error alert, stays connected)
- [ ] Handles rapid button taps (debounced, prevents multiple rapid starts)
- [ ] Handles microphone revoked mid-conversation (detected and handled by store)
- [ ] Handles network errors (shows user-friendly messages)

### AC10: Responsive Design
- [ ] Screen layout works on mobile (portrait and landscape)
- [ ] Screen layout works on tablet
- [ ] Screen layout works on web (PWA)
- [ ] Button and text remain readable at various screen sizes
- [ ] No overflow or clipping on smaller screens
- [ ] Proper margins and padding for spacing
- [ ] Safe area insets respected (notch, status bar, etc.)

---

## Tasks / Subtasks

### Task 1: Create Conversation Screen Component (AC1, AC2)
- [ ] Create file: `mobile/src/app/(tabs)/index.tsx`
- [ ] Import necessary React Native components: View, TouchableOpacity, Text, Alert, ActivityIndicator
- [ ] Import conversation store: `useConversationStore`
- [ ] Import audio service: `{ requestMicrophonePermission, checkMicrophonePermission }`
- [ ] Create functional component `ConversationScreen()`
- [ ] Set up basic layout structure with container, status text, and button

### Task 2: Implement Microphone Button (AC2, AC3)
- [ ] Create TouchableOpacity component for microphone button
- [ ] Implement button styling with large size (minimum 60x60)
- [ ] Add button label that changes based on connection state
- [ ] Add microphone icon inside button (can use Expo/React Native icon library)
- [ ] Implement tap handler: `handlePress()` function
- [ ] Ensure proper touch target size (48dp minimum for accessibility)

### Task 3: Integrate Store State (AC3, AC8)
- [ ] Call `useConversationStore()` hook in component
- [ ] Extract state: `{ isConnected, isLoading, isAISpeaking, error }`
- [ ] Extract actions: `{ startConversation, endConversation }`
- [ ] Update button styling based on `isConnected` state
- [ ] Update button label based on `isConnected` state
- [ ] Subscribe to store updates and trigger re-renders

### Task 4: Implement Permission Checking (AC4, AC5)
- [ ] In `handlePress()`: Check if starting or ending
- [ ] If starting:
  - [ ] Call `checkMicrophonePermission()` first
  - [ ] If not granted, call `requestMicrophonePermission()`
  - [ ] If still not granted, show Alert with settings link
  - [ ] If granted, call `store.startConversation()`
- [ ] If ending: Call `store.endConversation()`
- [ ] Handle errors from permission checks

### Task 5: Implement Connection Status Display (AC6)
- [ ] Add status text component above or below button
- [ ] Determine status message based on store state:
  - Not connected: "Tap to start conversation"
  - Loading: "Connecting to AI..."
  - Connected: "Connected - Speak now"
  - AI Speaking: "AI is speaking..." (if isAISpeaking true)
- [ ] Apply consistent styling to status text
- [ ] Update status text reactively when store state changes

### Task 6: Add Visual Feedback & Animations (AC7)
- [ ] Create microphone icon component or use icon library
- [ ] Implement pulsing animation when connected (using Animated or React Native animations)
- [ ] Implement loading spinner when connecting (ActivityIndicator or similar)
- [ ] Style button differently for each state:
  - Not connected: neutral color (gray/blue)
  - Connecting: loading appearance (spinner, disabled)
  - Connected: active color (highlight, pulsing)
  - AI Speaking: different color/animation
- [ ] Test animations for smoothness and performance

### Task 7: Error Handling & User Feedback (AC9)
- [ ] In permission denied case: Show Alert with clear message
- [ ] In start conversation error: Show Alert with error details
- [ ] In end conversation error: Show Alert (but keep UI in connected state for retry)
- [ ] Implement debouncing on button tap to prevent rapid fires
- [ ] Add error display on screen if store.error is set
- [ ] Test all error scenarios

### Task 8: Responsive Design & Layout (AC10)
- [ ] Test layout on mobile portrait (375px width)
- [ ] Test layout on mobile landscape (812px width)
- [ ] Test layout on tablet (768px width)
- [ ] Test layout on web/PWA (1024px+ width)
- [ ] Use flexbox for responsive centering
- [ ] Add appropriate padding and margins for all screen sizes
- [ ] Ensure button remains accessible on all sizes
- [ ] Test with different font scales (accessibility)

### Task 9: Integrate Icon Library (AC2, AC7)
- [ ] Choose icon library: @react-native-community/hooks or Expo vector icons
- [ ] Import microphone icon component
- [ ] Add icon to button with proper sizing
- [ ] Style icon to match button design
- [ ] Test icon rendering on all platforms

### Task 10: Testing (AC1-AC10)
- [ ] Manual test: Start conversation → Grant permission → See connected state
- [ ] Manual test: End conversation → See disconnected state
- [ ] Manual test: Deny permission → See error alert, button remains functional
- [ ] Manual test: Rapid taps → Verify debounce works
- [ ] Manual test: State changes → Verify UI updates correctly
- [ ] Manual test: Portrait/landscape orientation → Layout remains proper
- [ ] Test on web (PWA) → Verify works in browser
- [ ] Test on Android emulator → Verify works on mobile
- [ ] Test error scenarios → Verify error messages display

### Task 11: Documentation & Review (AC8)
- [ ] Add JSDoc comment to ConversationScreen component
- [ ] Document the expected store interface (what state/methods are used)
- [ ] Document permission flow in comments
- [ ] Document state transitions and visual feedback
- [ ] Review code for accessibility best practices
- [ ] Verify TypeScript types are correct
- [ ] Verify component follows project conventions

---

## Technical Notes

### Component Structure

```typescript
// mobile/src/app/(tabs)/index.tsx
import React, { useCallback } from 'react';
import {
  View,
  TouchableOpacity,
  Text,
  Alert,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { useConversationStore } from '../../stores/useConversationStore';
import {
  requestMicrophonePermission,
  checkMicrophonePermission,
} from '../../services/audio.service';
import { MicrophoneIcon } from '../../components/MicrophoneIcon';

export default function ConversationScreen() {
  const { isConnected, isLoading, isAISpeaking, error, startConversation, endConversation } =
    useConversationStore();

  const handlePress = useCallback(async () => {
    if (isConnected) {
      await endConversation();
    } else {
      try {
        // Check if permission already granted
        let hasPermission = await checkMicrophonePermission();

        // If not, request it
        if (!hasPermission) {
          hasPermission = await requestMicrophonePermission();
        }

        // If still not granted, show error
        if (!hasPermission) {
          Alert.alert(
            'Microphone Required',
            'Please enable microphone access in app settings to use voice conversations.'
          );
          return;
        }

        // Permission granted, start conversation
        await startConversation();
      } catch (err) {
        Alert.alert('Error', 'Failed to start conversation');
      }
    }
  }, [isConnected, startConversation, endConversation]);

  const getStatusMessage = () => {
    if (isLoading) return 'Connecting to AI...';
    if (isAISpeaking) return 'AI is speaking...';
    if (isConnected) return 'Connected - Speak now';
    return 'Tap to start conversation';
  };

  const getButtonStyle = () => {
    if (isLoading) return [styles.button, styles.buttonLoading];
    if (isConnected) return [styles.button, styles.buttonActive];
    return [styles.button, styles.buttonDefault];
  };

  return (
    <View style={styles.container}>
      <Text style={styles.status}>{getStatusMessage()}</Text>

      <TouchableOpacity
        style={getButtonStyle()}
        onPress={handlePress}
        disabled={isLoading}
        activeOpacity={0.7}
      >
        {isLoading ? (
          <ActivityIndicator size="large" color="#fff" />
        ) : (
          <MicrophoneIcon active={isConnected} />
        )}
      </TouchableOpacity>

      {error && <Text style={styles.error}>{error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  status: {
    fontSize: 16,
    marginBottom: 32,
    color: '#666',
  },
  button: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 32,
  },
  buttonDefault: {
    backgroundColor: '#e0e0e0',
  },
  buttonActive: {
    backgroundColor: '#4CAF50',
  },
  buttonLoading: {
    backgroundColor: '#2196F3',
  },
  error: {
    color: 'red',
    marginTop: 16,
    fontSize: 14,
  },
});
```

### Dependencies Already Available

- `react-native` - Core components
- `@react-native-async-storage/async-storage` - Storage (already used)
- `zustand` - State management (already used in conversation store)
- `expo-av` - Audio/microphone (already added in Story 3.6)
- Icon library options:
  - `@react-native-community/hooks` - Vector icons
  - Expo vector icons (if available)

### Key Integration Points

1. **Conversation Store** (`useConversationStore`):
   - State: `isConnected`, `isLoading`, `isAISpeaking`, `error`
   - Methods: `startConversation()`, `endConversation()`
   - The store handles: Daily.co connection, bot communication, error handling

2. **Audio Service** (`audio.service.ts`):
   - Already created in Story 3.6
   - Functions: `requestMicrophonePermission()`, `checkMicrophonePermission()`
   - Returns: `Promise<boolean>`

3. **Previous Story Dependencies**:
   - Story 3.5: `useConversationStore` with Zustand state
   - Story 3.6: Microphone permission service

### Design Decisions

- **Simple, Minimal UI**: Focus on voice interaction, not visual complexity
- **One Primary Button**: Microphone button is the main interaction point
- **Status Text**: Clear indication of what's happening
- **Permission Flow**: Always check before starting (user experience)
- **Error Resilience**: Graceful error handling, button remains functional

### Platform Considerations

- **Web (PWA)**: Uses browser notification system, standard web events
- **Mobile (Android/iOS)**: Uses native permission dialogs, platform-specific audio
- **Cross-Platform**: React Native components work on all platforms with styling adjustments

---

## Learnings from Previous Story

**From Story 3.6 (Microphone Permission & Setup) - Status: DONE**

- **New Service Created**: `audio.service.ts` with `requestMicrophonePermission()` and `checkMicrophonePermission()` functions available at `mobile/src/services/audio.service.ts`
  - **Key Functions**:
    - `requestMicrophonePermission(): Promise<boolean>` - Shows permission dialog, returns true if granted
    - `checkMicrophonePermission(): Promise<boolean>` - Non-intrusive check without dialog, returns true if already granted
  - **Pattern to Reuse**: Platform-specific branching (Platform.OS === 'web' vs mobile), nested try/catch error handling, __DEV__ guarded logging
  - **Web Implementation**: Uses `navigator.mediaDevices.getUserMedia()` and `navigator.permissions.query()`
  - **Mobile Implementation**: Uses Expo Audio API (`Audio.requestPermissionsAsync()`, `Audio.getPermissionsAsync()`)

- **Test Suite Created**: Comprehensive test file at `mobile/__tests__/services/audio.service.test.ts` with 30+ test cases
  - **Pattern to Reuse**: Jest mocking of platform APIs, testing both web and mobile paths
  - **Test Structure**: Mobile tests, web tests, error scenarios, platform detection, integration flows
  - **CI/CD Ready**: Tests follow Jest patterns, ready for automation

- **Architectural Pattern Established**: Permission handling before conversation start
  - **Recommended Integration**: Call `checkMicrophonePermission()` → if false, call `requestMicrophonePermission()` → if still false, show user alert
  - **Never Throws**: Both functions handle all errors gracefully, always return boolean

- **Critical Implementation Detail**: Media stream cleanup
  - **Web-specific**: After permission granted via `getUserMedia()`, immediately call `stream.getTracks().forEach(track => track.stop())`
  - **Prevents Resource Leaks**: Don't keep audio/video streams open after permission check

- **TypeScript Safety**: All functions have explicit `Promise<boolean>` return types, typed error catching

- **Pending Review Items Resolved**: Code review APPROVED with zero critical/high/medium issues

[Source: docs/stories/3-6-microphone-permission-setup.md#Dev-Agent-Record]

---

## Related Stories

- **Depends On:** Story 3.5 (Conversation store - provides startConversation method)
- **Depends On:** Story 3.6 (Microphone permission - provides permission service)
- **Prerequisite For:** Story 3.8 (Daily.co React Native integration)
- **Prerequisite For:** Story 3.9 (End conversation & cleanup)
- **Prerequisite For:** Story 3.10 (End-to-end voice test - uses this screen)

---

## Notes for Developer

1. **Use Story 3.6 Services**: Don't reimplement permission checking. Call `requestMicrophonePermission()` and `checkMicrophonePermission()` from `audio.service.ts`.

2. **Store Integration**: The `useConversationStore` (from Story 3.5) should handle all conversation logic. This screen only handles UI and permission flow.

3. **Icon Simplicity**: Start with simple UI. Consider using vector icon library (Expo icons or React Native community icons).

4. **Platform Consistency**: Test thoroughly on both web (PWA in browser) and mobile (Android emulator). UI should feel native on each platform.

5. **Accessibility**: Ensure button is large enough (48dp+), text is readable, animations don't cause motion sickness.

6. **Error Recovery**: When errors occur, keep the button functional so users can retry (except during critical failures).

7. **Visual Feedback**: Animation of pulsing microphone when connected is important UX signal. Use Animated API for smooth performance.

---

## Definition of Done

- [x] Conversation screen created in `mobile/src/app/(tabs)/index.tsx`
- [x] Microphone button implemented with proper styling and sizing
- [x] Button state management integrated with conversation store
- [x] Permission handling flow implemented (check → request → start)
- [x] Connection status display showing current state
- [x] Visual feedback and animations for state transitions
- [x] Error handling for all edge cases
- [x] Responsive design works on all screen sizes
- [x] Integration with `useConversationStore` complete
- [x] Integration with `audio.service.ts` complete
- [x] All 10 acceptance criteria met
- [x] All 11 tasks completed
- [x] Component follows TypeScript best practices
- [x] Component follows React Native patterns
- [x] Ready for integration testing with Story 3.8

---

## Dev Agent Record

### Context Reference

docs/stories/3-7-conversation-screen-ui.context.xml

### Agent Model Used

Claude Haiku 4.5

### Debug Log References

### Completion Notes List

### File List

---

## Change Log

**2025-11-10 - Initial Draft**
- Story created by create-story workflow
- 10 acceptance criteria defined
- 11 implementation tasks outlined
- Technical implementation example provided
- Learnings from Story 3.6 integrated
- Integration with existing components planned
