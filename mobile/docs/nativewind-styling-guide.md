# NativeWind v4 Styling Guide

## Technical Specification for Numerologist AI Mobile App

**Version:** 1.0
**Date:** 2025-11-08
**NativeWind Version:** 4.2.1
**Tailwind CSS Version:** 3.4.18

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Configuration](#configuration)
4. [Custom Theme](#custom-theme)
5. [Styling Patterns](#styling-patterns)
6. [Platform Support](#platform-support)
7. [Common Use Cases](#common-use-cases)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What is NativeWind?

NativeWind is a utility-first CSS framework for React Native that brings Tailwind CSS to the mobile development ecosystem. It processes Tailwind classes at **build time** and converts them into React Native StyleSheet objects, providing a seamless developer experience while maintaining native performance.

### Key Benefits

- **Unified Styling**: Use the same Tailwind classes across web and mobile platforms
- **Type Safety**: Full TypeScript support with autocomplete for className props
- **Performance**: Build-time processing means zero runtime overhead
- **Developer Experience**: Familiar Tailwind syntax with mobile-specific extensions
- **Custom Theming**: Extend with custom colors, spacing, typography, and more

### How It Works

```
Tailwind Classes (className) → NativeWind Babel Preset → React Native Styles
```

1. **Author**: Write components using `className` prop with Tailwind classes
2. **Transform**: Babel preset processes classes during build
3. **Output**: Native StyleSheet objects optimized for React Native

---

## Architecture

### Build-Time Processing Flow

```
┌─────────────────┐
│  Component      │
│  className="..."│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Babel Transform │  (nativewind/babel preset)
│ + PostCSS       │  (processes global.css)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Metro Bundler   │  (withNativeWind wrapper)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Native Styles   │  (StyleSheet objects)
└─────────────────┘
```

### File Dependencies

```
tailwind.config.js ──┐
                     ├─→ global.css ─→ PostCSS ─→ Metro (withNativeWind)
babel.config.js ─────┤
                     └─→ Babel Transform ─→ Components
```

---

## Configuration

### Required Dependencies

```json
{
  "nativewind": "^4.2.1",
  "tailwindcss": "3.4.18",
  "react-native-reanimated": "3.17.5",
  "react-native-worklets": "0.6.1",
  "react-native-worklets-core": "1.6.2"
}
```

**Version Notes:**
- ⚠️ NativeWind v4 only supports Tailwind CSS v3 (not v4)
- React Native Reanimated is required for animation utilities
- Worklets packages enable advanced animation features

### babel.config.js

```javascript
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      ["babel-preset-expo", { jsxImportSource: "nativewind" }],
      "nativewind/babel",
    ],
    plugins: [
      "react-native-reanimated/plugin",
    ],
  };
};
```

**Key Points:**
- `jsxImportSource: "nativewind"` enables className prop support
- NativeWind preset MUST be listed in presets array (not plugins)
- Reanimated plugin should be last in plugins array

### metro.config.js

```javascript
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: './global.css' });
```

**Key Points:**
- `withNativeWind` wrapper is essential for CSS processing
- `input: './global.css'` specifies the CSS entry point
- Metro will process CSS files through PostCSS pipeline

### postcss.config.js

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

**Key Points:**
- Uses standard `tailwindcss` plugin (NOT `@tailwindcss/postcss` from v4)
- Autoprefixer adds vendor prefixes for web compatibility

### global.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Import Location:**
- Import in `src/app/_layout.tsx` (root layout)
- Import BEFORE any component rendering

```typescript
import '../../global.css';
```

### Web Platform Configuration

For proper web dark mode support:

```typescript
// src/app/_layout.tsx
if (Platform.OS === 'web') {
  if (StyleSheet.configure) {
    StyleSheet.configure({ colorScheme: 'light' });
  }
}
```

Add to `app.json`:

```json
{
  "web": {
    "bundler": "metro"
  }
}
```

---

## Custom Theme

### tailwind.config.js Structure

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './App.{js,jsx,ts,tsx}',
    './src/**/*.{js,jsx,ts,tsx}',
    './app/**/*.{js,jsx,ts,tsx}',
  ],
  presets: [require('nativewind/preset')],
  theme: {
    extend: {
      // Custom theme extensions
    },
  },
  plugins: [],
};
```

### Color System

Our app uses a mystical, premium color palette optimized for numerology content:

```javascript
colors: {
  // Primary palette
  primary: {
    DEFAULT: '#d4af37', // Gold - represents wisdom & enlightenment
    dark: '#a8960b',
    light: '#f0d98f',
  },
  secondary: {
    DEFAULT: '#8b5cf6', // Purple - mystical & spiritual
    light: '#a78bfa',
    dark: '#7c3aed',
  },
  accent: '#5eead4', // Teal - balance & clarity

  // Semantic colors
  success: '#5eead4',
  warning: '#fbbf24',
  error: '#ef4444',
  info: '#60a5fa',

  // Backgrounds (dark theme)
  dark: '#0d0d1a',     // Primary background
  light: '#1a1a33',    // Secondary background
  card: '#1a1235',     // Card backgrounds
  elevated: '#2d1b69', // Elevated surfaces

  // Chat bubble backgrounds
  chat: {
    user: '#7C4DFF',          // Vibrant purple for user
    userLight: '#9575CD',
    assistant: '#FFCA28',     // Warm gold for assistant
    assistantLight: '#FFD54F',
  },

  // Text colors
  text: {
    primary: '#ffffff',       // Pure white for readability
    secondary: '#FFD54F',     // Bright warm gold
    muted: '#9E9E9E',        // Lighter gray for visibility
    inverse: '#0d0d1a',
    onPurple: '#ffffff',     // White text on purple
    onGold: '#1a1a33',       // Dark text on gold
  },

  // Borders
  border: {
    DEFAULT: '#333',
    focus: '#8b5cf6',
    error: '#ef4444',
  },
}
```

**Usage Examples:**

```jsx
// Primary gold button
<Pressable className="bg-primary">

// User message bubble
<View className="bg-chat-user">
  <Text className="text-text-onPurple">Message text</Text>
</View>

// Card with border
<View className="bg-card border border-border">
```

### Spacing System

Consistent spacing creates visual harmony:

```javascript
spacing: {
  xs: '4px',    // Minimal spacing
  sm: '8px',    // Compact spacing
  md: '16px',   // Default spacing
  lg: '24px',   // Comfortable spacing
  xl: '32px',   // Generous spacing
  xxl: '48px',  // Large spacing
  xxxl: '64px', // Extra large spacing
}
```

**Usage Pattern:**

```jsx
// Message cards with generous vertical spacing
<View className="mb-xl px-sm">

// Button padding
<Pressable className="px-lg py-md">

// Screen padding
<SafeAreaView className="p-lg">
```

### Typography System

Mobile-optimized font sizes with proper line heights:

```javascript
fontSize: {
  display: ['32px', { lineHeight: '38px', fontWeight: '700' }],
  h1: ['24px', { lineHeight: '32px', fontWeight: '700' }],
  h2: ['18px', { lineHeight: '24px', fontWeight: '600' }],
  body: ['16px', { lineHeight: '24px', fontWeight: '400' }],
  small: ['14px', { lineHeight: '20px', fontWeight: '400' }],
  tiny: ['12px', { lineHeight: '16px', fontWeight: '400' }],
}
```

**Usage Examples:**

```jsx
// Screen title
<Text className="text-h1 font-bold text-text-primary">
  Numerology Guide
</Text>

// Message text
<Text className="text-body leading-6 text-text-onPurple">
  Your message here
</Text>

// Timestamp
<Text className="text-tiny text-white/70">
  Just now
</Text>
```

### Shadow System

Subtle shadows add depth without overwhelming:

```javascript
boxShadow: {
  'gold': '0 10px 20px rgba(212, 175, 55, 0.3)',
  'gold-lg': '0 15px 30px rgba(212, 175, 55, 0.4)',
  'purple': '0 10px 20px rgba(139, 92, 246, 0.3)',
}
```

**Note:** For React Native, shadows must be combined with inline styles:

```jsx
<View
  className="shadow-md"
  style={{
    shadowColor: '#7C4DFF',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4, // Android shadow
  }}
>
```

---

## Styling Patterns

### Basic Component Styling

```jsx
import { View, Text } from 'react-native';

export function Card({ children }) {
  return (
    <View className="bg-card rounded-lg p-lg mb-md border border-border">
      <Text className="text-h2 font-bold text-text-primary mb-sm">
        Card Title
      </Text>
      {children}
    </View>
  );
}
```

### Conditional Classes

Use template literals for dynamic styling:

```jsx
export function MessageCard({ message, type, timestamp }) {
  const isUser = type === 'user';

  return (
    <View className={`mb-xl px-sm ${isUser ? 'items-end' : 'items-start'}`}>
      <View
        className={`
          max-w-[85%] px-md py-md rounded-[20px] shadow-md
          ${isUser ? 'bg-chat-user' : 'bg-chat-assistant'}
        `}
      >
        <Text className={`text-body leading-6 mb-xs ${
          isUser ? 'text-text-onPurple' : 'text-text-onGold'
        }`}>
          {message}
        </Text>
        <Text className={`text-tiny ${
          isUser ? 'text-white/70' : 'text-text-onGold/70'
        }`}>
          {timestamp}
        </Text>
      </View>
    </View>
  );
}
```

**Key Techniques:**
- Use ternary operators for binary conditions
- Multi-line template strings for readability
- Opacity with `/70` syntax for transparency

### Combining with Inline Styles

Some React Native features require inline styles (shadows, transforms):

```jsx
export function AnimatedCard({ children }) {
  const fadeAnim = useRef(new Animated.Value(0)).current;

  return (
    <Animated.View
      className="bg-card rounded-lg p-lg"
      style={{
        opacity: fadeAnim,
        transform: [{ scale: 1.05 }],
      }}
    >
      {children}
    </Animated.View>
  );
}
```

**Rule:** Use className for static styles, inline styles for dynamic/animated properties.

### Layout Patterns

#### Centered Content

```jsx
<View className="flex-1 justify-center items-center">
  <Text className="text-h1">Centered Text</Text>
</View>
```

#### Flex Row with Gap

```jsx
<View className="flex-row items-center gap-sm">
  <MaterialIcons name="auto-awesome" size={20} color="#d4af37" />
  <Text className="text-h2">Icon + Text</Text>
</View>
```

#### Scrollable Content with Fixed Bottom

```jsx
<SafeAreaView className="flex-1 bg-dark">
  <ScrollView className="flex-1 px-md py-md">
    {/* Content */}
  </ScrollView>

  <View className="items-center py-lg pb-xxl bg-dark border-t border-border/50">
    {/* Fixed button */}
  </View>
</SafeAreaView>
```

### State-Based Styling

```jsx
export function RecordButton({ onPress, isRecording, disabled }) {
  return (
    <Pressable
      className={`
        w-32 h-32 rounded-full items-center justify-center
        ${isRecording
          ? 'bg-error shadow-[0_10px_20px_rgba(239,68,68,0.3)]'
          : 'bg-primary shadow-gold'
        }
        ${disabled ? 'bg-gray-700 opacity-50' : ''}
      `}
      onPress={onPress}
      disabled={disabled}
    >
      <MaterialIcons name="mic" size={48} color={disabled ? '#666' : '#fff'} />
    </Pressable>
  );
}
```

### Form Validation Styling

```jsx
export function ValidatedInput({ value, error, ...props }) {
  return (
    <TextInput
      className={`
        border rounded-lg px-md py-md text-body text-text-primary
        ${error
          ? 'border-error bg-error/10'
          : 'border-border bg-light'
        }
      `}
      value={value}
      {...props}
    />
  );
}
```

---

## Platform Support

### Class Support Matrix

| Category | Web Support | Native Support | Example |
|----------|-------------|----------------|---------|
| **Layout** | ✅ Full | ✅ Full | `flex`, `flex-row`, `justify-center` |
| **Spacing** | ✅ Full | ✅ Full | `p-lg`, `m-xl`, `gap-sm` |
| **Typography** | ✅ Full | ✅ Full | `text-h1`, `font-bold`, `leading-6` |
| **Colors** | ✅ Full | ✅ Full | `bg-primary`, `text-text-primary` |
| **Borders** | ✅ Full | ✅ Full | `border`, `rounded-lg`, `border-error` |
| **Shadows** | ⚠️ Limited | ⚠️ Manual | Requires inline styles on native |
| **Opacity** | ✅ Full | ✅ Full | `opacity-50`, `text-white/70` |
| **Transforms** | ⚠️ Limited | ⚠️ Limited | Use Animated API instead |
| **Positioning** | ✅ Full | ⚠️ Partial | `absolute`, `relative` work differently |
| **Grid** | ✅ Full | ❌ None | Use `flex` instead |
| **Media Queries** | ✅ Full | ❌ None | Use Dimensions API or breakpoints |

### Platform-Specific Classes

```jsx
// Web-only classes
<View className="web:hover:bg-primary-dark web:cursor-pointer">

// Native-only classes
<View className="native:shadow-lg">

// Responsive by platform
<View className="w-full web:max-w-md">
```

### Handling Platform Differences

```jsx
import { Platform } from 'react-native';

export function CrossPlatformCard({ children }) {
  return (
    <View className="bg-card rounded-lg p-lg">
      {Platform.OS === 'web' ? (
        <div className="hover:bg-elevated transition-colors">
          {children}
        </div>
      ) : (
        <Pressable
          className="active:bg-elevated"
          onPress={handlePress}
        >
          {children}
        </Pressable>
      )}
    </View>
  );
}
```

---

## Common Use Cases

### 1. Chat Message Bubbles

**Requirements:**
- Different colors for user vs assistant
- Rounded corners for modern feel
- Proper text contrast
- Subtle shadows for depth
- Responsive width (max 85%)

**Implementation:**

```jsx
// src/components/conversation/MessageCard.tsx
export function MessageCard({ message, type, timestamp }) {
  const fadeAnim = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
  }, [fadeAnim]);

  const isUser = type === 'user';

  return (
    <Animated.View
      className={`mb-xl px-sm ${isUser ? 'items-end' : 'items-start'}`}
      style={{ opacity: fadeAnim }}
    >
      <View
        className={`
          max-w-[85%] px-md py-md rounded-[20px] shadow-md
          ${isUser ? 'bg-chat-user' : 'bg-chat-assistant'}
        `}
        style={{
          shadowColor: isUser ? '#7C4DFF' : '#FFCA28',
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.25,
          shadowRadius: 8,
          elevation: 4,
        }}
      >
        <Text className={`text-body leading-6 mb-xs ${
          isUser ? 'text-text-onPurple' : 'text-text-onGold'
        }`}>
          {message}
        </Text>
        <Text className={`text-tiny ${
          isUser ? 'text-white/70' : 'text-text-onGold/70'
        }`}>
          {timestamp}
        </Text>
      </View>
    </Animated.View>
  );
}
```

**Key Patterns:**
- `mb-xl` (32px) for generous spacing between messages
- `rounded-[20px]` for custom border radius
- Shadow colors match bubble backgrounds
- Fade-in animation on mount
- Conditional alignment (`items-end` vs `items-start`)

### 2. Animated Record Button

**Requirements:**
- Circular button with mic icon
- Pulsing animation when recording
- Expanding waveform rings
- Color change based on state
- Disabled state styling

**Implementation:**

```jsx
// src/components/conversation/RecordButton.tsx
export function RecordButton({ onPress, isRecording, disabled }) {
  const pulseAnim = React.useRef(new Animated.Value(1)).current;
  const wave1 = React.useRef(new Animated.Value(0)).current;
  const wave2 = React.useRef(new Animated.Value(0)).current;
  const wave3 = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    if (isRecording) {
      // Button pulsing
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.1,
            duration: 600,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 600,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ])
      ).start();

      // Waveform rings with staggered timing
      const createWaveAnimation = (wave, delay) => {
        return Animated.loop(
          Animated.sequence([
            Animated.delay(delay),
            Animated.timing(wave, {
              toValue: 1,
              duration: 1500,
              easing: Easing.out(Easing.ease),
              useNativeDriver: true,
            }),
            Animated.timing(wave, {
              toValue: 0,
              duration: 0,
              useNativeDriver: true,
            }),
          ])
        );
      };

      createWaveAnimation(wave1, 0).start();
      createWaveAnimation(wave2, 500).start();
      createWaveAnimation(wave3, 1000).start();
    } else {
      pulseAnim.setValue(1);
      wave1.setValue(0);
      wave2.setValue(0);
      wave3.setValue(0);
    }
  }, [isRecording, pulseAnim, wave1, wave2, wave3]);

  const getWaveStyle = (wave) => ({
    position: 'absolute',
    width: 160,
    height: 160,
    borderRadius: 80,
    borderWidth: 2,
    borderColor: isRecording ? '#ef4444' : '#d4af37',
    opacity: wave.interpolate({
      inputRange: [0, 1],
      outputRange: [0.7, 0],
    }),
    transform: [{
      scale: wave.interpolate({
        inputRange: [0, 1],
        outputRange: [0.8, 1.4],
      }),
    }],
  });

  return (
    <View className="items-center justify-center" style={{ width: 160, height: 160 }}>
      {isRecording && (
        <>
          <Animated.View style={getWaveStyle(wave1)} pointerEvents="none" />
          <Animated.View style={getWaveStyle(wave2)} pointerEvents="none" />
          <Animated.View style={getWaveStyle(wave3)} pointerEvents="none" />
        </>
      )}

      <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
        <Pressable
          className={`
            w-32 h-32 rounded-full items-center justify-center
            ${isRecording
              ? 'bg-error shadow-[0_10px_20px_rgba(239,68,68,0.3)]'
              : 'bg-primary shadow-gold'
            }
            ${disabled ? 'bg-gray-700 opacity-50' : ''}
          `}
          onPress={onPress}
          disabled={disabled}
        >
          <MaterialIcons name="mic" size={48} color={disabled ? '#666' : '#fff'} />
        </Pressable>
      </Animated.View>
    </View>
  );
}
```

**Key Patterns:**
- Multiple animated values for complex effects
- Staggered timing (0ms, 500ms, 1000ms) for wave sequence
- `pointerEvents="none"` prevents waves from blocking touches
- State-based class switching for colors

### 3. Collapsible Header

**Requirements:**
- Header with title and subtitle
- Expand/collapse animation
- Icon indicator for state
- Border separator
- Touch feedback

**Implementation:**

```jsx
// Excerpt from src/app/(tabs)/index.tsx
export default function ConversationScreen() {
  const [headerCollapsed, setHeaderCollapsed] = useState(false);
  const headerHeight = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.timing(headerHeight, {
      toValue: headerCollapsed ? 0 : 1,
      duration: 300,
      useNativeDriver: false, // Cannot use native driver for height
    }).start();
  }, [headerCollapsed, headerHeight]);

  return (
    <SafeAreaView className="flex-1 bg-dark">
      <View className="border-b border-border/50">
        <TouchableOpacity
          className="px-lg py-md flex-row items-center justify-between"
          onPress={() => setHeaderCollapsed(!headerCollapsed)}
          activeOpacity={0.7}
        >
          <View className="flex-1">
            <View className="flex-row items-center gap-sm">
              <MaterialIcons name="auto-awesome" size={20} color="#d4af37" />
              <Text className="text-h2 font-bold text-text-primary">
                Numerology Guide
              </Text>
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

      {/* Rest of component */}
    </SafeAreaView>
  );
}
```

**Key Patterns:**
- `useNativeDriver: false` required for height animations
- `overflow: 'hidden'` ensures smooth collapse
- Icon rotation via conditional rendering
- Border opacity with `/50` suffix

### 4. Form Validation

**Requirements:**
- Error state styling
- Focus state handling
- Inline error messages
- Accessible labels

**Implementation:**

```jsx
// Excerpt from src/app/(auth)/register.tsx
export default function RegisterScreen() {
  const [fieldErrors, setFieldErrors] = useState({});

  return (
    <SafeAreaView className="flex-1 bg-dark">
      <ScrollView className="flex-1 px-lg py-lg">
        <View className="mb-lg">
          <Text className="text-small font-semibold text-text-primary mb-xs">
            Email
          </Text>
          <TextInput
            className={`
              border rounded-lg px-md py-md text-body text-text-primary
              ${fieldErrors.email
                ? 'border-error bg-error/10'
                : 'border-border bg-light'
              }
            `}
            placeholder="Enter your email"
            placeholderTextColor="#9E9E9E"
            value={email}
            onChangeText={setEmail}
          />
          {fieldErrors.email && (
            <Text className="text-tiny text-error mt-xs">
              {fieldErrors.email}
            </Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
```

**Key Patterns:**
- Error background with low opacity (`bg-error/10`)
- Conditional border color
- Error message below input
- Consistent spacing with `mb-xs`, `mb-lg`

---

## Best Practices

### 1. Prefer className Over Inline Styles

✅ **Good:**
```jsx
<View className="bg-card rounded-lg p-lg border border-border" />
```

❌ **Bad:**
```jsx
<View style={{
  backgroundColor: '#1a1235',
  borderRadius: 8,
  padding: 24,
  borderWidth: 1,
  borderColor: '#333'
}} />
```

**Why:** className is more maintainable, type-safe, and leverages the theme system.

### 2. Use Theme Extensions, Not Hard-Coded Values

✅ **Good:**
```jsx
<Text className="text-text-primary">Hello</Text>
<View className="bg-primary" />
```

❌ **Bad:**
```jsx
<Text style={{ color: '#ffffff' }}>Hello</Text>
<View style={{ backgroundColor: '#d4af37' }} />
```

**Why:** Theme ensures consistency and makes global changes easier.

### 3. Combine Classes Logically

✅ **Good:**
```jsx
<View className={`
  flex-1 bg-card
  ${active ? 'border-primary' : 'border-border'}
`} />
```

❌ **Bad:**
```jsx
<View className={active ? 'flex-1 bg-card border-primary' : 'flex-1 bg-card border-border'} />
```

**Why:** Reduces duplication and improves readability.

### 4. Use Semantic Spacing

✅ **Good:**
```jsx
<View className="mb-xl px-sm"> {/* 32px margin, 8px padding */}
```

❌ **Bad:**
```jsx
<View className="mb-8 px-2"> {/* Raw Tailwind values */}
```

**Why:** Semantic naming (`xs`, `sm`, `md`, etc.) ensures consistency across the app.

### 5. Leverage Opacity Syntax

✅ **Good:**
```jsx
<Text className="text-white/70">Muted text</Text>
<View className="border-border/50" />
```

❌ **Bad:**
```jsx
<Text style={{ color: 'rgba(255, 255, 255, 0.7)' }}>Muted text</Text>
```

**Why:** Cleaner syntax and works with theme colors.

### 6. Keep Shadows Platform-Aware

✅ **Good:**
```jsx
<View
  className="shadow-md"
  style={{
    shadowColor: '#7C4DFF',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4, // Android
  }}
/>
```

❌ **Bad:**
```jsx
<View className="shadow-lg" /> {/* Won't work as expected on native */}
```

**Why:** React Native requires explicit shadow properties and Android elevation.

### 7. Use Arbitrary Values Sparingly

✅ **Acceptable:**
```jsx
<View className="max-w-[85%] rounded-[20px]">
```

⚠️ **Use with caution:**
```jsx
<View className="p-[17px] mb-[23px]"> {/* Non-standard values */}
```

**Why:** Arbitrary values should only be used for design-specific requirements not in the theme.

### 8. Organize Classes by Category

✅ **Good:**
```jsx
<View className="
  flex-1 items-center justify-center
  bg-card rounded-lg
  p-lg mb-xl
  border border-border
">
```

**Order:** Layout → Visual → Spacing → Borders

### 9. Use Animated API for Complex Animations

✅ **Good:**
```jsx
<Animated.View
  className="bg-card rounded-lg p-lg"
  style={{ opacity: fadeAnim }}
/>
```

❌ **Bad:**
```jsx
<View className="animate-fade-in" /> {/* Limited animation support */}
```

**Why:** React Native Animated API provides better performance and control.

### 10. Test Across Platforms

Always test styling on:
- iOS simulator/device
- Android emulator/device
- Web browser (if applicable)

Platform differences in rendering can be subtle but important.

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Classes Not Applied

**Symptoms:** className has no effect on component

**Possible Causes:**
- Babel preset not configured correctly
- Metro bundler not using withNativeWind
- Component not in tailwind.config.js content paths
- Build cache not cleared

**Solution:**
```bash
# Clear cache and rebuild
rm -rf node_modules/.cache
npx expo start --clear
```

Verify babel.config.js has:
```javascript
presets: [
  ["babel-preset-expo", { jsxImportSource: "nativewind" }],
  "nativewind/babel",
]
```

#### 2. Custom Colors Not Working

**Symptoms:** `bg-primary` shows no color

**Solution:**
Check that tailwind.config.js has:
```javascript
presets: [require('nativewind/preset')],
```

And verify color is in theme.extend.colors, not theme.colors (which would override defaults).

#### 3. Babel Plugin Error

**Symptoms:** `.plugins is not a valid Plugin property`

**Cause:** Babel trying to parse CSS files

**Solution:**
Ensure metro.config.js uses withNativeWind:
```javascript
module.exports = withNativeWind(config, { input: './global.css' });
```

#### 4. Tailwind v4 Compatibility Error

**Symptoms:** `NativeWind only supports Tailwind CSS v3`

**Solution:**
Downgrade Tailwind CSS:
```bash
npm install -D tailwindcss@3.4.18
npm uninstall @tailwindcss/postcss
```

Update postcss.config.js:
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},  // NOT @tailwindcss/postcss
    autoprefixer: {},
  },
};
```

#### 5. Missing Worklets Error

**Symptoms:** `Cannot find module 'react-native-worklets/plugin'`

**Solution:**
Install required dependencies:
```bash
npm install react-native-reanimated@3.17.5
npm install react-native-worklets@0.6.1
npm install react-native-worklets-core@1.6.2
```

Add to babel.config.js plugins:
```javascript
plugins: [
  "react-native-reanimated/plugin",
]
```

#### 6. Web Color Scheme Error

**Symptoms:** `Cannot manually set color scheme, as dark mode is type 'media'`

**Solution:**
Add to root layout (_layout.tsx):
```typescript
if (Platform.OS === 'web') {
  if (StyleSheet.configure) {
    StyleSheet.configure({ colorScheme: 'light' });
  }
}
```

Add to app.json:
```json
{
  "web": {
    "bundler": "metro"
  }
}
```

#### 7. Shadows Not Visible on Android

**Symptoms:** shadow-* classes have no effect on Android

**Solution:**
Always include elevation property:
```jsx
<View
  className="shadow-lg"
  style={{ elevation: 4 }}
/>
```

#### 8. TypeScript Errors on className

**Symptoms:** Type error: Property 'className' does not exist

**Solution:**
Ensure nativewind-env.d.ts exists in project root:
```typescript
/// <reference types="nativewind/types" />
```

And it's referenced in tsconfig.json:
```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true
  }
}
```

---

## Migration Checklist

### Converting StyleSheet to NativeWind

When converting existing components:

- [ ] Import className types if using TypeScript
- [ ] Replace StyleSheet.create with NativeWind classes
- [ ] Convert numeric spacing to semantic tokens (8 → `sm`, 16 → `md`)
- [ ] Move colors to theme if not already defined
- [ ] Keep inline styles only for animations and shadows
- [ ] Test on iOS, Android, and web
- [ ] Remove unused StyleSheet imports
- [ ] Update component snapshots/tests

**Example Migration:**

**Before (StyleSheet):**
```jsx
import { View, Text, StyleSheet } from 'react-native';

export function Card({ title }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1a1235',
    borderRadius: 8,
    padding: 24,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#333',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
  },
});
```

**After (NativeWind):**
```jsx
import { View, Text } from 'react-native';

export function Card({ title }) {
  return (
    <View className="bg-card rounded-lg p-lg mb-md border border-border">
      <Text className="text-h2 font-semibold text-text-primary mb-sm">
        {title}
      </Text>
    </View>
  );
}
```

**Benefits:**
- 60% less code
- Type-safe with autocomplete
- Consistent with design system
- Easier to maintain
- Hot reload friendly

---

## Appendix

### Quick Reference

#### Most Used Classes

```
Layout:       flex-1, flex-row, items-center, justify-center, gap-sm
Spacing:      p-lg, px-md, py-sm, m-xl, mb-md, mt-xs
Colors:       bg-card, bg-primary, text-text-primary, border-border
Typography:   text-h1, text-body, text-tiny, font-bold, leading-6
Visual:       rounded-lg, rounded-full, shadow-md, opacity-50
Sizing:       w-full, h-32, max-w-[85%]
```

#### Color Palette Reference

```
Primary:      #d4af37 (gold)
Secondary:    #8b5cf6 (purple)
Accent:       #5eead4 (teal)
Dark BG:      #0d0d1a
Card BG:      #1a1235
User Bubble:  #7C4DFF (purple)
AI Bubble:    #FFCA28 (gold)
Error:        #ef4444 (red)
Success:      #5eead4 (teal)
```

#### Spacing Scale

```
xs:   4px
sm:   8px
md:   16px
lg:   24px
xl:   32px
xxl:  48px
xxxl: 64px
```

#### File Location Reference

```
Configuration:
  /tailwind.config.js       - Theme & extensions
  /babel.config.js          - Babel presets
  /metro.config.js          - Metro bundler
  /postcss.config.js        - PostCSS plugins
  /global.css               - CSS entry point

Components:
  /src/components/          - Reusable components
  /src/app/(tabs)/          - Tab screens
  /src/app/(auth)/          - Auth screens
  /src/app/_layout.tsx      - Root layout (imports global.css)
```

---

## Conclusion

This guide provides a comprehensive reference for NativeWind v4 styling in the Numerologist AI mobile app. Key takeaways:

1. **Configuration is critical** - Babel, Metro, and PostCSS must be properly set up
2. **Use the theme system** - Custom colors, spacing, and typography ensure consistency
3. **Platform awareness** - Some features require inline styles or platform-specific handling
4. **Patterns over repetition** - Leverage reusable styling patterns for common UI elements
5. **Test across platforms** - iOS, Android, and web can render differently

For questions or issues not covered here, consult:
- [NativeWind Documentation](https://www.nativewind.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Native Documentation](https://reactnative.dev/)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Maintained By:** Development Team
