# Story 2.9: Profile Screen UI

Status: drafted

## Story

As a **logged-in user**,
I want **to view my profile information**,
so that **I can see my account details**.

## Acceptance Criteria

1. **AC1**: Profile screen component created in `mobile/src/app/(tabs)/profile.tsx`
2. **AC2**: Displays user information: Name, Email, Birth Date
3. **AC3**: Shows formatted birth date (e.g., "May 15, 1990")
4. **AC4**: "Logout" button that calls `useAuthStore.logout()`
5. **AC5**: On logout, clears token and navigates to login screen
6. **AC6**: Loading state while fetching user data
7. **AC7**: Error handling if user data fails to load
8. **AC8**: Clean, readable layout

## Tasks / Subtasks

- [ ] **Task 1**: Set Up Profile Screen Component Structure (AC: #1)
  - [ ] 1.1: Create `mobile/src/app/(tabs)/profile.tsx` file
  - [ ] 1.2: Import required React Native components: View, Text, TouchableOpacity, SafeAreaView, ActivityIndicator
  - [ ] 1.3: Import useAuthStore from stores
  - [ ] 1.4: Import useRouter from expo-router
  - [ ] 1.5: Set up component state: loading, error, user data retrieval

- [ ] **Task 2**: Implement User Data Display (AC: #2, #3)
  - [ ] 2.1: Get current user data from useAuthStore
  - [ ] 2.2: Create card layout to display user information
  - [ ] 2.3: Display full name from user profile
  - [ ] 2.4: Display email address
  - [ ] 2.5: Display birth date formatted as readable string (e.g., "May 15, 1990")
  - [ ] 2.6: Use date-fns for date formatting

- [ ] **Task 3**: Implement Logout Functionality (AC: #4, #5)
  - [ ] 3.1: Get logout method from useAuthStore
  - [ ] 3.2: Create handleLogout async function
  - [ ] 3.3: Call logout() from useAuthStore
  - [ ] 3.4: On logout success, navigate to /(auth)/login using router.replace()
  - [ ] 3.5: Handle logout errors gracefully

- [ ] **Task 4**: Implement Loading State (AC: #6)
  - [ ] 4.1: Add loading state variable
  - [ ] 4.2: Show ActivityIndicator while loading user data
  - [ ] 4.3: Disable logout button while loading
  - [ ] 4.4: Show loading text or skeleton state

- [ ] **Task 5**: Implement Error Handling (AC: #7)
  - [ ] 5.1: Add error state variable
  - [ ] 5.2: Display error message if user data fails to load
  - [ ] 5.3: Provide option to retry loading user data
  - [ ] 5.4: Handle missing user data gracefully

- [ ] **Task 6**: Design and Style Profile Screen (AC: #8)
  - [ ] 6.1: Create StyleSheet with consistent spacing and layout
  - [ ] 6.2: Use React Native StyleSheet for performance
  - [ ] 6.3: Design card-based layout for user information
  - [ ] 6.4: Style logout button with danger/primary color
  - [ ] 6.5: Add appropriate padding and margins
  - [ ] 6.6: Ensure responsive design for various screen sizes
  - [ ] 6.7: Match visual style with login and register screens
  - [ ] 6.8: Add SafeAreaView for mobile to avoid notch/status bar

- [ ] **Task 7**: Implement Tabs Navigation Integration (AC: #1)
  - [ ] 7.1: Verify profile.tsx is automatically discoverable by Expo Router
  - [ ] 7.2: Verify profile screen appears in tabs layout
  - [ ] 7.3: Test navigation to/from profile screen via tabs
  - [ ] 7.4: Verify proper stack-in-tabs nesting

- [ ] **Task 8**: Integration Testing (AC: all)
  - [ ] 8.1: Test successful profile data load and display
  - [ ] 8.2: Test logout functionality
  - [ ] 8.3: Test navigation to login after logout
  - [ ] 8.4: Test loading state display
  - [ ] 8.5: Test error state display
  - [ ] 8.6: Test date formatting for various dates
  - [ ] 8.7: Test logout button disabled during submission
  - [ ] 8.8: Test retry functionality for failed data loading
  - [ ] 8.9: Test tab navigation to profile screen
  - [ ] 8.10: Test profile screen layout on various device sizes

## Dev Notes

### Learnings from Previous Story

**From Story 2-8-register-screen-ui (Status: done)**

- **Auth Store Integration**: `mobile/src/stores/useAuthStore.ts` provides:
  - `logout()` method available for clearing authentication
  - `user` or current user data accessible from store
  - Token auto-cleared in SecureStore on logout

- **Component Patterns Established**:
  - Error container styling (red banner with error message)
  - Loading state UI with ActivityIndicator
  - Form layouts with ScrollView and KeyboardAvoidingView
  - StyleSheet performance optimization approach

- **Navigation Patterns**:
  - Use `router.replace()` after logout to prevent back navigation to profile
  - Expo Router file-based routing works automatically

- **Date Handling**:
  - User birth date stored as ISO string (YYYY-MM-DD) in auth store
  - Format to readable display using date-fns or toLocaleDateString()

- **Dependencies Already Installed**:
  - zustand@^5.0.8 (state management)
  - expo-router (file-based routing)
  - @expo/vector-icons (MaterialIcons)
  - @react-native-community/datetimepicker (already added in 2.8)

- **Testing Framework**:
  - Jest with @testing-library/react-native
  - Mock patterns established for auth store, router, and components

[Source: stories/2-8-register-screen-ui.md#Dev-Agent-Record]

### Technical Summary

This story implements the profile screen UI, allowing authenticated users to view their account information and logout. It builds on the authentication infrastructure created in Epic 2 (Stories 2.1-2.8).

**Key Implementation Points:**

1. **Expo Router Tabs Integration**:
   - Profile screen automatically discovered as route at `/profile`
   - Accessible via tabs navigation layout from `mobile/src/app/(tabs)/_layout.tsx`
   - Part of protected screens (only visible when authenticated)

2. **User Data Display**:
   - Display user name, email, and birth date from auth store
   - Format birth date using date-fns library (e.g., "May 15, 1990")
   - Simple card-based layout for clean readability
   - User data already available from Story 2.5 (Get Current User endpoint)

3. **Logout Functionality**:
   - Call `useAuthStore.logout()` method
   - Logout clears auth token from SecureStore
   - After logout, navigate to `/(auth)/login` using `router.replace()` to prevent back navigation
   - User is automatically unauthenticated and routed by root layout

4. **Loading and Error States**:
   - Loading state while fetching/refreshing user data
   - Error state for failed data loads with retry option
   - ActivityIndicator for visual feedback
   - Disable logout button during submission

5. **Responsive Design**:
   - Works on mobile (iOS/Android) and web
   - SafeAreaView for mobile notch avoidance
   - Responsive spacing and text sizing
   - Consistent styling with login/register screens

6. **Date Formatting**:
   - Birth date stored as ISO string (YYYY-MM-DD) in backend
   - Display as readable format: "May 15, 1990"
   - Use date-fns `format()` or native `toLocaleDateString()`

### Project Structure Notes

**File Locations**:
- **CREATE**: Profile screen: `mobile/src/app/(tabs)/profile.tsx` (new file)
- **USE**: Auth store: `mobile/src/stores/useAuthStore.ts` (from Story 2.6)
- **USE**: Tabs layout: `mobile/src/app/(tabs)/_layout.tsx` (created in Story 2.9 or earlier)

**Expo Router Structure** (File-Based Routing):
```
mobile/src/app/
  ├── _layout.tsx              # Root layout (auth checking)
  ├── (auth)/                  # Auth group (login/register)
  │   ├── _layout.tsx          # Auth stack
  │   ├── login.tsx
  │   └── register.tsx
  └── (tabs)/                  # Protected tabs (home, history, profile)
      ├── _layout.tsx          # Tabs layout
      ├── index.tsx            # Home/Conversation
      ├── history.tsx          # History
      └── profile.tsx          # Profile (THIS STORY)
```

**Auth Store Interface** (from Story 2.6):
```typescript
interface User {
  id: string;
  email: string;
  full_name: string;
  birth_date: string;  // ISO format: YYYY-MM-DD
}

// useAuthStore methods:
- logout(): Promise<void>
- user: User | null
- isAuthenticated: boolean
```

**Tab Navigation Wiring**:
```typescript
// File: mobile/src/app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{ title: 'Conversation' }} />
      <Tabs.Screen name="history" options={{ title: 'History' }} />
      <Tabs.Screen name="profile" options={{ title: 'Profile' }} />
    </Tabs>
  );
}
```

### Profile Screen Layout Example

```typescript
// Conceptual layout structure
<SafeAreaView>
  <ScrollView>
    {loading && <ActivityIndicator />}

    {error && <ErrorBanner message={error} onRetry={handleRetry} />}

    {user && (
      <View style={styles.profileCard}>
        <Text style={styles.label}>Name</Text>
        <Text style={styles.value}>{user.full_name}</Text>

        <Text style={styles.label}>Email</Text>
        <Text style={styles.value}>{user.email}</Text>

        <Text style={styles.label}>Birth Date</Text>
        <Text style={styles.value}>{formattedBirthDate}</Text>
      </View>
    )}

    <TouchableOpacity
      style={styles.logoutButton}
      onPress={handleLogout}
      disabled={loading}
    >
      <Text style={styles.logoutButtonText}>Logout</Text>
    </TouchableOpacity>
  </ScrollView>
</SafeAreaView>
```

### Date Formatting Implementation

```typescript
import { format } from 'date-fns';

// Assuming birthDate from auth store is ISO string: "1990-05-15"
const formattedBirthDate = format(
  new Date(user.birth_date),
  'MMMM d, yyyy'
);  // Result: "May 15, 1990"

// Alternative without date-fns:
const date = new Date(user.birth_date);
const formattedBirthDate = date.toLocaleDateString('en-US', {
  year: 'numeric',
  month: 'long',
  day: 'numeric'
});
```

### Logout Handler Implementation

```typescript
const handleLogout = async () => {
  try {
    setIsSubmitting(true);
    await logout();

    // Router automatically handles navigation via auth check in root layout
    // Or explicitly navigate:
    router.replace('/(auth)/login');
  } catch (err: any) {
    setError(err.message || 'Logout failed. Please try again.');
  } finally {
    setIsSubmitting(false);
  }
};
```

### Styling Approach

**React Native StyleSheet** (Consistent with Auth Screens):
```typescript
import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContent: {
    flexGrow: 1,
    padding: 20,
  },
  profileCard: {
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  label: {
    fontSize: 12,
    color: '#666',
    marginTop: 12,
    marginBottom: 4,
    fontWeight: '600',
  },
  value: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  logoutButton: {
    backgroundColor: '#FF3B30',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 24,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  errorContainer: {
    backgroundColor: '#ffebee',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#ef5350',
  },
  errorText: {
    color: '#c62828',
    fontSize: 14,
  },
});
```

### Testing Checklist

**Manual Testing**:
1. **Profile Display**:
   - [ ] Navigate to profile tab
   - [ ] See user name, email, birth date displayed
   - [ ] Birth date formatted correctly (e.g., "May 15, 1990")
   - [ ] Information matches account details entered during registration

2. **Logout Functionality**:
   - [ ] Click logout button
   - [ ] See loading state briefly
   - [ ] Automatically navigate to login screen
   - [ ] Cannot go back to profile screen
   - [ ] Token cleared from secure storage

3. **Error Handling**:
   - [ ] Simulate error loading user data
   - [ ] See error message displayed
   - [ ] Click retry button
   - [ ] Successfully load data after retry

4. **Loading State**:
   - [ ] See activity indicator when loading
   - [ ] Logout button disabled during loading
   - [ ] Text unchanged while loading

5. **Navigation**:
   - [ ] Tabs layout shows profile tab
   - [ ] Can navigate between tabs (home, history, profile)
   - [ ] Profile accessible from any tab
   - [ ] Logout removes profile from available screens

6. **Cross-Platform**:
   - [ ] Works on web browser
   - [ ] Works on iOS simulator/device
   - [ ] Works on Android simulator/device
   - [ ] Responsive on different screen sizes

### References

- [Source: docs/epics.md#Story-2.9] - Original story requirements
- [Source: stories/2-8-register-screen-ui.md] - Register screen patterns and styling
- [Source: stories/2-7-login-screen-ui.md] - Login screen patterns
- [Source: stories/2-6-frontend-auth-state-management-zustand.md] - Auth store implementation
- [Expo Router Docs](https://docs.expo.dev/router/introduction/) - File-based routing
- [date-fns Documentation](https://date-fns.org/) - Date formatting library
- [React Native SafeAreaView](https://reactnative.dev/docs/safeareaview) - Mobile notch handling

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude Haiku 4.5 (claude-haiku-4-5-20251001)

### Debug Log References

### Completion Notes List

### File List
