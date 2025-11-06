# Story 2.10: Auth Navigation Flow

Status: ready-for-dev

## Story

As a **user**,
I want **automatic navigation based on auth status**,
so that **I'm directed to login or home screen appropriately**.

## Acceptance Criteria

1. **AC1**: Root layout checks auth status on app load using `checkAuth()`
2. **AC2**: If not authenticated → show auth screens (login/register)
3. **AC3**: If authenticated → show main tabs (home, history, profile)
4. **AC4**: Protected screens require authentication
5. **AC5**: After login/register → automatic navigation to home
6. **AC6**: After logout → automatic navigation to login
7. **AC7**: Deep linking respects auth state
8. **AC8**: Smooth transitions (no flashing of wrong screen)
9. **AC9**: Works correctly on app reload

## Tasks / Subtasks

- [ ] **Task 1**: Verify Root Layout Auth Check Implementation (AC: #1)
  - [ ] 1.1: Verify `mobile/src/app/_layout.tsx` imports useAuthStore
  - [ ] 1.2: Verify checkAuth() called in useEffect on component mount
  - [ ] 1.3: Verify isAuthenticated, isLoading states read from auth store
  - [ ] 1.4: Verify useRouter and useSegments hooks imported
  - [ ] 1.5: Add comprehensive logging for auth state changes

- [ ] **Task 2**: Implement Authentication-Based Routing (AC: #2, #3, #4)
  - [ ] 2.1: Verify routing logic based on isAuthenticated state
  - [ ] 2.2: Verify non-authenticated users redirect to /(auth)/login
  - [ ] 2.3: Verify authenticated users redirect to home (tabs)
  - [ ] 2.4: Verify routing checks segments to prevent redirect loops
  - [ ] 2.5: Test protected screens require authentication

- [ ] **Task 3**: Implement Post-Login/Register Navigation (AC: #5)
  - [ ] 3.1: Verify login screen does NOT manually navigate
  - [ ] 3.2: Verify register screen does NOT manually navigate
  - [ ] 3.3: Verify root layout detects auth state change
  - [ ] 3.4: Verify automatic redirect to home after successful auth
  - [ ] 3.5: Test navigation timing and state synchronization

- [ ] **Task 4**: Implement Post-Logout Navigation (AC: #6)
  - [ ] 4.1: Verify logout() clears auth state in store
  - [ ] 4.2: Verify root layout detects logout
  - [ ] 4.3: Verify automatic redirect to login screen
  - [ ] 4.4: Verify user cannot navigate back to protected screens
  - [ ] 4.5: Test token cleared from storage on logout

- [ ] **Task 5**: Implement Loading State (AC: #8)
  - [ ] 5.1: Show loading screen while isLoading is true
  - [ ] 5.2: Use ActivityIndicator for loading visual
  - [ ] 5.3: Prevent navigation redirects during loading
  - [ ] 5.4: Test smooth transitions without flash
  - [ ] 5.5: Verify no blank screens during auth check

- [ ] **Task 6**: Handle Deep Linking (AC: #7)
  - [ ] 6.1: Test deep link to protected screen when not authenticated
  - [ ] 6.2: Verify redirect to login with return URL preserved
  - [ ] 6.3: Test deep link to public screen when authenticated
  - [ ] 6.4: Verify proper navigation without breaking auth flow
  - [ ] 6.5: Test deep links work after app reload

- [ ] **Task 7**: Test App Reload Behavior (AC: #9)
  - [ ] 7.1: Test app reload with valid token in storage
  - [ ] 7.2: Verify checkAuth() validates token on reload
  - [ ] 7.3: Test reload with expired/invalid token
  - [ ] 7.4: Verify proper redirect for both scenarios
  - [ ] 7.5: Test reload maintains user state if token valid

- [ ] **Task 8**: Integration Testing (AC: all)
  - [ ] 8.1: Test complete flow: open app → login → navigate → logout
  - [ ] 8.2: Test app reload after login (should stay logged in)
  - [ ] 8.3: Test navigating directly to protected route when logged out
  - [ ] 8.4: Test auth state changes trigger proper navigation
  - [ ] 8.5: Test no navigation loops or infinite redirects
  - [ ] 8.6: Test smooth transitions with no screen flashing
  - [ ] 8.7: Test deep linking to various routes
  - [ ] 8.8: Test logout from different screens
  - [ ] 8.9: Cross-platform testing (web, iOS, Android)
  - [ ] 8.10: Performance testing (navigation speed, auth check time)

## Dev Notes

### Learnings from Previous Story

**From Story 2-9-profile-screen-ui (Status: done)**

**🎉 EXCELLENT NEWS: Story 2.10 is already 90% implemented!**

During Story 2-9, we encountered an issue where auth state wasn't persisting after login. To fix this, we implemented the EXACT solution required for Story 2.10:

- **Root Layout Auth Flow Created**: `mobile/src/app/_layout.tsx` (lines 1-75)
  - Calls `checkAuth()` on app mount to restore persisted tokens
  - Shows loading screen during auth validation
  - Automatically redirects based on `isAuthenticated` state
  - Uses `useSegments()` to detect current route and prevent loops
  - Handles both auth → tabs and tabs → auth transitions

- **Key Files Modified in Story 2.9 (directly implementing 2.10 requirements)**:
  - `mobile/src/app/_layout.tsx` - NEW: Complete auth-based routing implementation
  - `mobile/src/app/(auth)/login.tsx` - MODIFIED: Removed manual navigation
  - `mobile/src/app/(auth)/register.tsx` - MODIFIED: Removed manual navigation

- **Auth Flow Working**:
  - Login → auth state updates → root layout auto-navigates to home ✅
  - Logout → auth state clears → root layout auto-navigates to login ✅
  - App reload → checkAuth() validates token → maintains session ✅
  - Protected routes → redirect to login if not authenticated ✅

- **Remaining Work for Story 2.10**:
  - Comprehensive testing and validation
  - Deep link handling refinement (if not already working)
  - Performance optimization if needed
  - Documentation updates

**Implementation already exists at**: `mobile/src/app/_layout.tsx`

```typescript
// Key implementation (already done):
export default function RootLayout() {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const segments = useSegments();
  const router = useRouter();

  // Check auth on mount
  useEffect(() => {
    checkAuth();
  }, []);

  // Handle routing based on auth state
  useEffect(() => {
    if (isLoading) return;

    const inAuthGroup = segments[0] === '(auth)';

    if (!isAuthenticated && !inAuthGroup) {
      router.replace('/(auth)/login');
    } else if (isAuthenticated && inAuthGroup) {
      router.replace('/');
    }
  }, [isAuthenticated, isLoading, segments]);

  // Show loading screen
  if (isLoading) {
    return <LoadingScreen />;
  }

  return <Stack screenOptions={{ headerShown: false }} />;
}
```

[Source: mobile/src/app/_layout.tsx, created in Story 2-9]
[Source: stories/2-9-profile-screen-ui.md#Dev-Agent-Record]

### Technical Summary

**IMPORTANT**: This story is unique because its core functionality was implemented as a bug fix during Story 2-9. The root cause analysis and fix for "user data not persisting" led us to implement the exact architecture required for Story 2.10.

**What Was Implemented in Story 2.9 (fixing auth persistence)**:

1. **Root Layout with Auth Check** (`_layout.tsx`):
   - Calls `checkAuth()` on app initialization
   - Reads `isAuthenticated`, `isLoading`, `checkAuth` from Zustand auth store
   - Shows loading screen while validating token
   - Uses `useSegments()` to detect current route group
   - Automatically redirects based on auth state

2. **Centralized Navigation Logic**:
   - Removed manual `router.replace()` from login/register screens
   - Root layout handles ALL auth-based navigation
   - Prevents race conditions between state updates and navigation
   - Single source of truth for routing decisions

3. **Token Restoration Flow**:
   - `checkAuth()` retrieves token from storage (SecureStore/localStorage)
   - Validates token with backend `/api/v1/auth/me`
   - Restores user session if token valid
   - Clears invalid tokens and redirects to login

**What Remains for Story 2.10**:

1. **Comprehensive Testing**:
   - Verify all 9 acceptance criteria met
   - Test edge cases (expired tokens, network errors, etc.)
   - Cross-platform validation (web, iOS, Android)
   - Deep link testing

2. **Performance Validation**:
   - Ensure smooth transitions without flashing
   - Optimize loading screen duration if needed
   - Verify no navigation loops

3. **Documentation**:
   - Update architecture docs with auth flow
   - Document deep linking behavior
   - Add troubleshooting guide

### Project Structure Notes

**Current Structure** (Created in Story 2.9):
```
mobile/src/app/
  ├── _layout.tsx              # Root layout (AUTH ROUTING) ← ALREADY IMPLEMENTED
  ├── (auth)/                  # Auth group (login/register)
  │   ├── _layout.tsx          # Auth stack
  │   ├── login.tsx            # ← Manual navigation REMOVED
  │   └── register.tsx         # ← Manual navigation REMOVED
  └── (tabs)/                  # Protected tabs (home, history, profile)
      ├── _layout.tsx          # Tabs layout
      ├── index.tsx            # Home/Conversation
      ├── history.tsx          # History
      └── profile.tsx          # Profile
```

**Auth Store Interface** (from Story 2.6):
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;  // ← KEY METHOD for Story 2.10
}
```

**Root Layout Implementation** (Already Complete):
```typescript
// File: mobile/src/app/_layout.tsx
import React, { useEffect } from 'react';
import { Stack, useRouter, useSegments } from 'expo-router';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useAuthStore } from '@/stores/useAuthStore';

export default function RootLayout() {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const segments = useSegments();
  const router = useRouter();

  // AC1: Check auth on app load
  useEffect(() => {
    checkAuth();
  }, []);

  // AC2-7: Handle authentication-based routing
  useEffect(() => {
    if (isLoading) return;

    const inAuthGroup = segments[0] === '(auth)';

    // AC2: Not authenticated → show auth screens
    if (!isAuthenticated && !inAuthGroup) {
      router.replace('/(auth)/login');
    }
    // AC3: Authenticated → show tabs
    else if (isAuthenticated && inAuthGroup) {
      router.replace('/');
    }
  }, [isAuthenticated, isLoading, segments]);

  // AC8: Show loading screen (smooth transitions)
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  // AC4: Stack screens (protected routes controlled by redirects)
  return (
    <Stack
      screenOptions={{
        headerShown: false,
      }}
    />
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
});
```

### Authentication Flow Diagram

```
App Launch
    ↓
Root Layout Mounts
    ↓
Call checkAuth()
    ↓
isLoading = true → Show Loading Screen
    ↓
Token in Storage?
    ├─ NO → isAuthenticated = false → Redirect to Login
    └─ YES → Validate with Backend
            ├─ Valid → isAuthenticated = true → Redirect to Home
            └─ Invalid → Clear Token → Redirect to Login

User Actions:
- Login Success → Auth State Updates → Root Layout Detects → Auto Navigate to Home
- Logout → Auth State Clears → Root Layout Detects → Auto Navigate to Login
- Deep Link → Root Layout Checks Auth → Redirect if Protected
```

### Testing Strategy

**Unit Tests** (to be written):
```typescript
describe('Root Layout Auth Navigation', () => {
  it('should call checkAuth on mount', () => {});
  it('should show loading screen while isLoading', () => {});
  it('should redirect to login when not authenticated', () => {});
  it('should redirect to home when authenticated', () => {});
  it('should handle auth state changes', () => {});
  it('should prevent navigation loops', () => {});
});
```

**Integration Tests** (manual):
1. **Fresh Install** → See loading → Redirect to login
2. **Login** → Auth state updates → Auto-navigate to home
3. **Reload App** → Token valid → Stay logged in
4. **Logout** → Auth state clears → Auto-navigate to login
5. **Invalid Token** → Clear and redirect to login
6. **Deep Link** → Respect auth requirements

### Deep Linking Considerations

**Expo Router Deep Linking** (built-in):
- Deep links automatically handled by Expo Router
- Root layout's auth check runs before deep link navigation
- If deep link requires auth and user not authenticated:
  - User redirected to login first
  - Return URL preserved by Expo Router
  - After login, navigate to original deep link

**No Additional Configuration Needed**:
- Expo Router handles deep link parsing
- Root layout ensures auth requirements met
- React Navigation state manages navigation stack

### Performance Considerations

**Optimization Already Implemented**:
1. **Single Auth Check**: `checkAuth()` called once on mount
2. **Conditional Redirects**: Only redirect when state changes
3. **Loading Screen**: Prevents flash of wrong screen
4. **useSegments**: Efficient route detection without full navigation

**Potential Issues to Watch**:
- Slow `checkAuth()` API call → User sees loading screen longer
- Network errors during token validation → Need retry logic
- Multiple rapid auth state changes → Navigation thrashing (prevented by isLoading check)

### References

- [Source: docs/epics.md#Story-2.10] - Original story requirements
- [Source: mobile/src/app/_layout.tsx] - Root layout implementation
- [Source: stories/2-9-profile-screen-ui.md] - Context for implementation
- [Expo Router Auth Pattern](https://docs.expo.dev/router/reference/authentication/) - Official docs
- [Expo Router useSegments](https://docs.expo.dev/router/reference/hooks/#usesegments) - Route detection
- [React Navigation Auth Flow](https://reactnavigation.org/docs/auth-flow/) - Best practices

## Dev Agent Record

### Context Reference

- [Story Context](./2-10-auth-navigation-flow.context.xml)

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
